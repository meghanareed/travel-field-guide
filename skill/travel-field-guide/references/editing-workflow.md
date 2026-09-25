# Editing workflow

The trip data lives inside `index.html` as a minified JSON blob between
`/*DATA:BEGIN*/` and `/*DATA:END*/`. Never hand-edit that blob. Edit the JSON,
then rebuild.

## Standard loop

```
python3 scripts/build.py --extract index.html -o trip.json   # skip if trip.json is already in the repo
# … edit trip.json (by hand or with a Python script, below) …
python3 scripts/build.py trip.json -o index.html             # validates, then writes atomically
node scripts/validate.js index.html
```

`build.py` refuses to write when validation fails (day numbering, iso/weekday
mismatches, unknown leg keys, duplicate shopping ids…), and it encodes to
bytes before writing to a temp file it then swaps in, so a failure never
leaves a 0-byte `index.html`.

Keep `trip.json` committed next to `index.html` so the next edit starts from
it. If the two ever disagree, the `index.html` is what travelers have — extract
from it.

## Scripted edits (Python)

For structural changes (reordering a tour, inserting a day, bulk map links),
load, mutate and dump the JSON rather than string-editing:

```python
import json
from urllib.parse import quote
M = lambda q: "https://www.google.com/maps/search/?api=1&query=" + quote(q)

t = json.load(open("trip.json", encoding="utf-8"))
d = t["days"][2]
d["tour"]["stops"].insert(2, {"name": "Miradouro da Graça", "url": M("Miradouro da Graça Lisbon"),
                               "address": "Largo da Graça, Lisbon", "addressUrl": M("Largo da Graça Lisbon"),
                               "desc": "…"})
json.dump(t, open("trip.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
```

## The emoji gotcha

Never write an astral emoji as a surrogate pair in Python source
(`"🎟"`) — `.encode('utf-8')` then throws "surrogates not allowed".
Use the real character (`"🎟️"`) or a full code point (`"\U0001F39F️"`).
BMP symbols like `⭐` are fine either way. `build.py` will fail loudly rather
than corrupt the file, but fix it at the source.

## Common edits

**Add a day in the middle.** Insert the day object, then renumber: every later
day's `n`, `iso`, `weekday`, `date`, `short` shift by one; bump `meta.tripEnd`,
`meta.dates`, `meta.nightsLabel`, and `glance.route` nights. Recheck
weekday-dependent notes. `build.py` catches any iso/weekday you miss.

**Swap two days.** Move only content fields (`leg, headline, subtitle,
overview, weather, walking, transport, schedule, tour, callouts, eat, foods,
good`); keep `n, weekday, date, iso, short` with the slot.

**Reorder a walking tour into a loop.** Decide circle vs furthest-first from
the hotel location; rebuild `tour.stops` in geographic order (core, then
`(optional)`, with `transit:true` connectors between legs); rewrite the
`schedule` to follow the same path; update `tour.intro` with the logic. After
the trip has started, reordering shifts `seen:` indices — warn the user.

**Split a driver/transfer day.** Keep one day; add a `tour` whose stops are the
morning city, a `transit:true` connector for the drive (driver name, time,
pickup), then the afternoon city. Put the booking itself in `bookings`.

**Add a shopping list or person.** Append to `shopping.lists` with a new,
stable `id`. One list hides the person switcher; add a second to show it.

**Add a new leg/country.** Add it to `legs`, tag the days/cities/foods/route
rows with its key, pick a color from `design-system.md`.

## Engine changes (template.html)

Changes to views, CSS or tabs go in `assets/template.html` (or the built app's
non-DATA code) with exact, unique string replacements. Keep to five tabs —
add capability with a `.seg` segmented switch, not a sixth tab. Rebuild every
trip that should pick up the change. After engine edits, run `validate.js`
against `assets/trip.example.json` *and* a real trip.

## Legacy apps (no DATA markers)

Earlier hand-built apps declare `const DATA = {…};` directly and hard-code
countries, dates and day counts in the JS. To edit one in place:

```python
import re, json, os
html = open(path, encoding="utf-8").read()
m = re.search(r'(const DATA\s*=\s*)(\{.*?\})(;\s*\n)', html, re.S)
data = json.loads(m.group(2))
# … mutate …
body = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
out = (html[:m.start()] + m.group(1) + body + m.group(3) + html[m.end():]).encode("utf-8")
open(path + ".tmp", "wb").write(out); os.replace(path + ".tmp", path)
```

To migrate one onto this engine instead: extract `DATA`, add `meta.tripStart`
(from its trip-start logic), build `legs` from its `LEGS` map, set each day's
`leg` from `DAY_LEG`, each city's `leg` from `CITY_LEG`, each `foods` group's
`leg` from `FOODS_BY_LEG`, each `glance.route` row's `leg`, move `SHOPPING`
to `shopping`, `drivers` → `bookings`, and the album link to `album`. Then
build and validate; compare the two apps side by side before replacing.
