---
name: travel-field-guide
description: >-
  Build or edit a self-contained, offline-capable mobile travel-companion web
  app for ANY trip — a single index.html "field guide" with per-day
  itineraries, a live departure-board "Today" screen, tappable Google-Maps
  walking tours, transit connectors, packing and shopping checklists,
  per-device save, and a shareable trip log. Starts from a placeholder trip
  JSON + a generic template and a build script, so a new trip is "fill in the
  JSON, run build.py". Use whenever the user wants a travel app, trip
  companion, itinerary app, or "field guide" to host on GitHub Pages and share
  with fellow travelers, OR when editing an app built from it — adding stops,
  days, cities, restaurants, shopping lists, callouts; reordering a walking
  tour; splitting a driver day. Trigger on casual phrasings like "turn my
  itinerary into an app," "make a field guide for our Japan trip," "add a day
  to my trip app," or "make the Lisbon walk a loop."
---

# Travel Field-Guide (generic)

A single-file, offline-first mobile web app that turns any multi-day trip into
a tappable "field guide." One `index.html` — vanilla HTML/CSS/JS, no build
step at runtime, no dependencies, no web fonts — so it works offline once
cached and drops straight onto GitHub Pages for a whole travel group.

The **engine** (`assets/template.html`) is trip-agnostic. **Everything**
trip-specific — title, dates, legs/colors, days, hotels, emergency numbers,
shopping lists, album link — lives in one JSON object. A new trip is:

```
cp assets/trip.example.json my-trip/trip.json   # fill in the placeholders
python3 scripts/build.py my-trip/trip.json -o my-trip/index.html
node scripts/validate.js my-trip/index.html
```

## Workflow

### New trip

1. **Gather the source material.** Itinerary doc, bookings, hotel list,
   flights, who's traveling. Ask only for what you can't infer: trip dates,
   cities in order, hotels, and anything booked (flights, drivers, tours).
2. **Copy `assets/trip.example.json`.** It is a complete, valid 4-day/2-leg
   skeleton where every value is a `[bracketed placeholder]`. Replace every
   placeholder; delete sections that don't apply (empty sections are hidden
   automatically — no packing → no Packing list, no `shopping.lists` → no
   Shopping switch, no `album.url` → no album card).
3. **Define `legs` first** — one per country/region the trip moves through,
   each `{name, flag, color}`. Then tag every day, city, food group and route
   row with a leg key. `transit` is built in (neutral brown) for travel days.
   Pick leg colors from `references/design-system.md` so they sit on the paper.
4. **Write the days** (`references/data-model.md` has every field). Days are
   numbered 1..N and `iso` must equal `tripStart + (n-1)` — the build checks
   this and the weekday, so date slips are caught.
5. **Research, don't invent.** Verify opening days against the actual trip
   weekdays, transit times, whether a shop/restaurant still exists. Correct a
   flawed premise kindly rather than parroting it (rule 5 below).
6. **Build + validate**, then deliver `index.html` and tell the user how to
   deploy (bottom of this file).

`build.py --check` validates without writing. It warns while any
`[placeholder]` text remains — ship only when that warning is gone.

### Editing an existing app

- Built from this template (has `/*DATA:BEGIN*/`)? Round-trip it:
  `build.py --extract index.html -o trip.json` → edit the JSON → rebuild.
  Keep `trip.json` next to `index.html` in the repo so later edits are easy.
- Older app without the markers (e.g. an earlier hand-built trip)? Follow the
  in-place pattern in `references/editing-workflow.md`, or migrate it: extract
  its `DATA`, map it onto the schema in `references/data-model.md`, and build.

## Non-negotiable rules

### 1. Walking-tour routing — a loop, or furthest-first-then-back
Order every day's `tour.stops` as a deliberate walk **from the hotel** (or the
arrival station on a day trip):
- **A circle** (preferred): out one side to the furthest point, cross/turn,
  back the other side to **end near the hotel**.
- **Furthest-first**: start at the point furthest from the hotel and work back.

Never zig-zag. When you reorder, fix the day's `schedule` so its times follow
the same path, and state the loop logic in `tour.intro`. Exception: a
crowd-sensitive sight can open the route "first thing" — say why.

### 2. Optional stops go last and are labeled "(optional)"
Core walk stays tight; extras (markets, second museums, shops) are appended
with `(optional)` in the name.

### 3. Use transit connectors between legs
When a day covers two places, insert `{transit:true, name, desc, url}` between
them. It renders as an unnumbered connector with no Seen toggle and is excluded
from the stop count. Optional `icon` (default 🚆; use 🚐 ⛴️ 🚠 ✈️ as fits).

### 4. Every stop is tappable to a map
`url` (and `addressUrl`) as Google Maps **search** links:
`https://www.google.com/maps/search/?api=1&query=<URL-encoded place + city>`.
Prefer a precise address; name + city is an acceptable fallback. Preserve any
verbatim URLs the source provided.

### 5. Be honest in recommendations
Verify current facts (opening days vs. the trip's actual weekdays, transport,
whether a place exists) before asserting them. Flag uncertainty in a callout
rather than stating a guess as fact.

### 6. Edit safely
Never hand-edit the minified DATA blob. Use `build.py` (extract → edit JSON →
build), which encodes before writing and swaps atomically. Never write astral
emoji as `\uXXXX\uXXXX` surrogate pairs in Python — use real characters or
`\U0001Fxxx`. See `references/editing-workflow.md`.

### 7. Stable ids
Shopping list `id`s and day numbers are part of saved-state keys on travelers'
phones. Rename `label`, never `id`. Reordering stops after the trip has started
shifts `seen:` indices — warn the user.

## Validate every change

```
node scripts/validate.js path/to/index.html            # add --shots DIR for 390px screenshots
```
It clicks all five tabs and every day, checks stop numbering (1..K, transit
unnumbered) against the data, verifies Seen + packing checks survive a reload,
exercises the shopping switch, and fails on any console error. If the bundled
Playwright browser is missing, set `PW_CHROMIUM=/path/to/chromium`.

## Deliver / deploy (tell the user)

- **GitHub Pages**: repo with `index.html` (+ `trip.json`) at the root →
  Settings → Pages → Deploy from branch `main` / root → link at
  `https://<user>.github.io/<repo>/` (case-sensitive; may 404 for a minute).
- **Offline**: open the link once, then **Add to Home Screen**. Also download
  Google Maps offline areas for each city.
- **Share**: one QR code of the Pages link for the group chat.
- Checkmarks, notes and Seen toggles are **per device**, not synced.
- The hosted copy only changes when the new `index.html` is pushed/uploaded.

## Reference files

- `references/data-model.md` — every field of the trip JSON, with shapes.
- `references/design-system.md` — the night-train look, tokens, leg palette.
- `references/editing-workflow.md` — build/extract round-trip, in-place edits, gotchas.
- `assets/template.html` — the engine (DATA slot + `{{PAGE_TITLE}}`-style head placeholders).
- `assets/trip.example.json` — the placeholder trip to copy.
- `scripts/build.py` — validate + build + extract.
- `scripts/validate.js` — headless smoke test.
