#!/usr/bin/env python3
"""Build a travel field-guide app from a trip JSON file.

    python3 build.py trip.json -o index.html          # build
    python3 build.py trip.json --check                # validate only
    python3 build.py --extract index.html -o trip.json  # pull DATA back out

The template (assets/template.html by default) holds the app engine and a
`/*DATA:BEGIN*/{}/*DATA:END*/` slot. The trip JSON is validated, serialized
into that slot, and the <head> placeholders ({{PAGE_TITLE}} etc.) are filled
from `meta`. Writes are encode-first + atomic, so a failure never leaves a
truncated file behind.
"""
import argparse
import datetime as dt
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_TEMPLATE = os.path.join(HERE, "..", "assets", "template.html")
SLOT = re.compile(r"/\*DATA:BEGIN\*/.*?/\*DATA:END\*/", re.S)
WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def validate(trip):
    """Return (errors, warnings). Errors block the build."""
    E, W = [], []
    meta = trip.get("meta") or {}
    legs = trip.get("legs") or {}
    days = trip.get("days") or []
    leg_keys = set(legs) | {"transit"}

    for k in ("title", "tripStart"):
        if not meta.get(k):
            E.append(f"meta.{k} is required")
    for k, leg in legs.items():
        for f in ("name", "flag", "color"):
            if not leg.get(f):
                E.append(f"legs.{k}.{f} is required")
    if not days:
        E.append("days is empty")

    start = None
    try:
        start = dt.date.fromisoformat(meta.get("tripStart", ""))
    except ValueError:
        E.append("meta.tripStart must be YYYY-MM-DD")

    for i, d in enumerate(days):
        tag = f"days[{i}]"
        if d.get("n") != i + 1:
            E.append(f"{tag}.n is {d.get('n')!r}, expected {i + 1} (days must be numbered 1..N in order)")
        for f in ("headline", "iso", "weekday", "date", "short"):
            if not d.get(f):
                E.append(f"{tag}.{f} is required")
        if d.get("leg", "transit") not in leg_keys:
            E.append(f"{tag}.leg {d.get('leg')!r} is not a key in legs")
        try:
            iso = dt.date.fromisoformat(d.get("iso", ""))
            if start and iso != start + dt.timedelta(days=i):
                E.append(f"{tag}.iso {iso} should be {start + dt.timedelta(days=i)} (tripStart + {i})")
            if d.get("weekday") and d["weekday"] != WEEKDAYS[iso.weekday()]:
                E.append(f"{tag}.weekday says {d['weekday']} but {iso} is a {WEEKDAYS[iso.weekday()]}")
        except ValueError:
            E.append(f"{tag}.iso must be YYYY-MM-DD")
        tour = d.get("tour")
        if tour:
            for j, s in enumerate(tour.get("stops") or []):
                if not s.get("name"):
                    E.append(f"{tag}.tour.stops[{j}] has no name")
                elif not s.get("url") and not s.get("transit"):
                    W.append(f"{tag}.tour.stops[{j}] '{s['name']}' has no map url")
            if not tour.get("intro"):
                W.append(f"{tag}.tour has no intro (state the loop / furthest-first logic)")
    if meta.get("tripEnd") and start and days:
        try:
            end = dt.date.fromisoformat(meta["tripEnd"])
            if end != start + dt.timedelta(days=len(days) - 1):
                W.append(f"meta.tripEnd {end} doesn't match the last day ({start + dt.timedelta(days=len(days) - 1)})")
        except ValueError:
            E.append("meta.tripEnd must be YYYY-MM-DD")

    for c in trip.get("cities") or []:
        if c.get("leg", "transit") not in leg_keys:
            E.append(f"cities '{c.get('city')}' leg {c.get('leg')!r} is not a key in legs")
    for f in trip.get("foods") or []:
        if f.get("leg") not in leg_keys:
            E.append(f"foods leg {f.get('leg')!r} is not a key in legs")

    ids = set()
    for l in (trip.get("shopping") or {}).get("lists") or []:
        if not l.get("id"):
            E.append(f"shopping list '{l.get('label')}' needs a stable id")
        elif l["id"] in ids:
            E.append(f"shopping list id {l['id']!r} is duplicated")
        ids.add(l.get("id"))

    blob = json.dumps(trip, ensure_ascii=False)
    if "[" in blob and re.search(r'"\[[^"\]]+\]', blob):
        W.append("trip still contains [bracketed] placeholder text")
    return E, W


def atomic_write(path, text):
    payload = text.encode("utf-8")  # encode FIRST — fails here, before touching the file
    tmp = path + ".tmp"
    with open(tmp, "wb") as f:
        f.write(payload)
    os.replace(tmp, path)


def build(trip, template):
    body = json.dumps(trip, ensure_ascii=False, separators=(",", ":"))
    body = body.replace("</", "<\\/")  # never close the <script> early
    if "/*DATA:END*/" in body:
        raise SystemExit("trip data contains the DATA:END marker")
    if not SLOT.search(template):
        raise SystemExit("template has no /*DATA:BEGIN*/…/*DATA:END*/ slot")
    out = SLOT.sub(lambda _: "/*DATA:BEGIN*/" + body + "/*DATA:END*/", template, count=1)
    meta = trip.get("meta") or {}
    fills = {
        "PAGE_TITLE": meta.get("pageTitle") or f"{meta.get('subtitle') or meta.get('title', 'Trip')} · Travel Companion",
        "APP_NAME": meta.get("appName") or meta.get("subtitle") or "Trip",
        "DESCRIPTION": meta.get("description") or f"Private travel companion — {meta.get('title', '')}",
    }
    for k, v in fills.items():
        out = out.replace("{{" + k + "}}", html.escape(v, quote=True))
    return out


def extract(path):
    text = open(path, encoding="utf-8").read()
    m = SLOT.search(text)
    if not m:
        raise SystemExit(f"{path}: no DATA slot found (not built from this template?)")
    raw = m.group(0)[len("/*DATA:BEGIN*/"):-len("/*DATA:END*/")]
    return json.loads(raw.replace("<\\/", "</"))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("trip", nargs="?", help="trip JSON file")
    ap.add_argument("-o", "--out", help="output file (default: index.html next to the trip JSON)")
    ap.add_argument("-t", "--template", default=DEFAULT_TEMPLATE)
    ap.add_argument("--check", action="store_true", help="validate only")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--extract", metavar="INDEX_HTML", help="write the DATA from a built app back out as JSON")
    a = ap.parse_args()

    if a.extract:
        data = extract(a.extract)
        text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
        if a.out:
            atomic_write(a.out, text)
            print(f"wrote {a.out}")
        else:
            sys.stdout.write(text)
        return

    if not a.trip:
        ap.error("trip JSON is required")
    trip = json.load(open(a.trip, encoding="utf-8"))
    errors, warnings = validate(trip)
    for w in warnings:
        print("warning:", w, file=sys.stderr)
    for e in errors:
        print("error:", e, file=sys.stderr)
    if errors or (a.strict and warnings):
        sys.exit(1)
    if a.check:
        print(f"ok — {len(trip['days'])} days, {len(warnings)} warning(s)")
        return

    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.trip)), "index.html")
    atomic_write(out, build(trip, open(a.template, encoding="utf-8").read()))
    print(f"wrote {out} ({len(trip['days'])} days)")


if __name__ == "__main__":
    main()
