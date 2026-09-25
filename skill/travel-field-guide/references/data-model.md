# Trip data model

The whole trip is one JSON object. `build.py` injects it into the template as
`const DATA`. Every top-level section except `meta`, `legs` and `days` is
optional — omitted or empty sections are hidden in the app.

```
{ meta, legs, days, glance, hotels, bookings, cities, foods,
  transport, packing, emergency, album, shopping }
```

`assets/trip.example.json` is a complete, valid example of every section.

## meta (required)

| key | used for |
|---|---|
| `title` * | Long trip title, e.g. `"Portugal · Spain"` — trip-log header |
| `subtitle` | Trip name, e.g. `"Iberian Summer"` — top-bar title |
| `appName` | Short Home-Screen name (≤ 12 chars) and download filename |
| `pageTitle` | `<title>`; default `"<subtitle> · Travel Companion"` |
| `description` | `<meta name=description>` |
| `brandCode` | Mono eyebrow in the top bar, e.g. `"PT · ES"` |
| `dates` | Human range, e.g. `"May 3–12, 2027"` |
| `nightsLabel` | Days-list eyebrow, e.g. `"9 nights · 2 countries"` |
| `summary` | Sentence on the pre-trip Today screen (route overview) |
| `tripStart` * | `YYYY-MM-DD` of Day 1 — drives Today's countdown/live day |
| `tripEnd` | `YYYY-MM-DD` of the last day (checked against the day count) |
| `bookingsTitle` | Heading for `bookings` on Info (default "Tours & transfers") |
| `storageId` | Saved-state namespace; default `tripStart` (see bottom) |

## legs (required)

```
"legs": { "pt": {"name":"Portugal","flag":"🇵🇹","color":"#2F6B4F"},
          "es": {"name":"Spain","flag":"🇪🇸","color":"#A8423C"} }
```
A leg is a country/region segment. Its `color` becomes the accent for any
day/city tagged with it; `flag` + `name` fill the top-bar pill. `transit`
(`✈ In transit`, `#7A6A52`) always exists — tag travel days with it; you can
override it by defining `legs.transit` yourself.

## days (required)

```
{
  "n": 3, "weekday":"Sunday", "date":"July 12", "iso":"2026-07-12", "short":"Sun, Jul 12",
  "leg": "pt",
  "headline":"Day Trip — Sintra", "subtitle":"Palaces in the hills",
  "overview":"1–3 sentences", "weather":"Avg ~24°C / 75°F", "walking":"~8 km, hilly",
  "transport":"Train from Rossio ~40 min",
  "schedule":[ {"time":"8:00","plan":"Walk to Rossio station"}, … ],
  "tour": { "intro":"loop logic…", "stops":[ …stops… ] } | null,
  "callouts":[ {"title":"🎟️ Book Pena ahead","body":"…"} ],
  "eat":[ {"cat":"☕ Coffee","rec":"Place","notes":"why"} ],
  "foods":[ {"name":"Travesseiro","desc":"…"} ],
  "good":{ "photo":"…", "coffee":"…", "restrooms":"…", "rainy":"…", "packing":"…" }
}
```
- `n` must run 1..N in order; `iso` must equal `tripStart + (n-1)`; `weekday`
  must match `iso`. `build.py` enforces all three.
- `n, weekday, date, iso, short` are **slot** fields. To swap two days' plans,
  move only the content fields and keep the slot fields — then recheck
  weekday-dependent notes (markets, Sunday/Monday closures).
- `tour: null` on pure travel days; `callouts` carry the plan instead.
- `good` keys are fixed; include only the ones you have.

### Stops

```
{ "name":"Pena Palace", "url":"<maps search url>", "address":"Estrada da Pena, 2710-609 Sintra",
  "addressUrl":"<maps search url>", "desc":"1–4 sentences of shareable detail." }
```
Transit connector between legs of a day:
```
{ "transit":true, "name":"Sintra → Cascais by bus", "icon":"🚌",
  "url":"<maps url>", "desc":"Bus 403, ~1 hr, every 30 min…" }
```
Optional stops: `(optional)` in the name, placed after the core route.

## glance

```
"glance": {
  "route":   [ {"nights":"May 3–6 (3)","city":"Lisbon","hotel":"…","leg":"pt"} ],
  "flights": [ {"k":"✈  Outbound","v":"Sat, May 3 — JFK → LIS, TP 208"} ],
  "key":     [ "Flights booked", "All hotels confirmed" ]   // "Confirmed" card before the trip
}
```

## hotels

`[ {name, address, mapUrl, phone, notes} ]` — Places tab; phone becomes a Call button.

## bookings

Drivers, tours, transfers, tastings (Info tab). `drivers` is accepted as an alias.
```
{ "title":"🚐  Lisbon → Seville transfer", "when":"Thu, May 8 — 9:00 AM",
  "detail": { "Pickup":"Hotel lobby", "Payment":"Prepaid" },   // any label → value pairs, in order
  "stops": [ {"name":"Évora (optional)","url":"…","desc":"…"} ] }
```

## cities

```
{ "city":"Lisbon", "leg":"pt",
  "links":[ {"label":"Hotel","t":"…","u":"<maps>"}, {"label":"Station","t":"…","u":"…"} ],
  "attractions":[ {"t":"Belém Tower","u":"<maps>","note":"short note"} ],
  "restaurants":[ {"t":"…","u":"…","note":"…"} ] }
```
Link labels `Hotel` / `Station` / `Airport` get 🏨 / 🚆 / ✈️; a link with no
`u` renders as a flat chip (e.g. "Driver pickup 9:00").

## foods

`[ {"leg":"pt","items":[{name,desc}]} ]` — shown as "Local specialties" inside
each city accordion of that leg.

## transport

```
"transport": {
  "tables":[ {"name":"Airport transfers",
              "tables":[ [["Option","Time","Cost"],["Metro","25 min","€1.80"]] ],   // first row = header
              "bullets":["…"]} ],
  "notes":[ {"title":"🚆 Tip","body":"…"} ] }
```

## packing

`[ {"title":"🎒  Carry-on","items":["Passport", …]} ]` — each becomes a checklist.
Include a "🏨 Hotel checkout" list; it's used at every move.

## emergency

```
{ "general":"112", "generalScope":"works everywhere on this trip", "generalLabel":"All countries",
  "numbers":[ {"country":"Portugal","police":"112","amb":"112"} ],
  "embassyLabel":"US embassy", "embassyFlag":"🇺🇸",
  "hospitals":[ {"city":"Lisbon","hospital":"Hospital de Santa Maria, …","embassy":"U.S. Embassy: Av. das Forças Armadas, +351 21 727 3300"} ],
  "money":[ {"k":"💶  Currency","v":"…"}, {"k":"🔌  Power","v":"…"} ] }
```
The first `+NN …` phone number inside `embassy` becomes a tap-to-call link.
Set `embassyLabel`/`embassyFlag` to the travelers' own nationality.

## album

`{ "url":"https://…", "label":"Open shared photo album", "note":"…" }` — omit to hide.

## shopping

```
{ "tip":"banner above each list (optional)", "whyLabel":"Why buy it here",
  "priceNote":"Prices are rough guides…",
  "lists":[ { "id":"mom", "label":"Mom", "flag":"🇫🇷", "accent":"#A8423C",
              "note":"Where to shop", "hideTip":false,
              "tiers":[ {"title":"⭐ Must","items":[
                  {"n":"Name","p":"€18–22","d":"what it does","s":"shade (optional)","w":"why buy here (optional)"} ]} ] } ] }
```
`id` is part of the saved-check keys — never rename it. One list hides the
person switcher; zero lists hides Shopping entirely.

## Saved state (localStorage, per device)

| key | what |
|---|---|
| `pk:<listIdx>:<itemIdx>` | packing checks |
| `buy:<listId>:<tierIdx>:<itemIdx>` | shopping checks |
| `note:day:<n>` | per-day notes |
| `seen:<dayN>:<stopIdx>` | Seen toggles (index includes transit rows) |

Keys are stored as `tfg:<storageId>:<key>`. `storageId` defaults to
`meta.tripStart`; set `meta.storageId` explicitly (e.g. `"iberia-2027"`) if two
trips could share a start date. The prefix matters because every repo under
`<user>.github.io` shares one origin — and one localStorage. Changing
`storageId` after travelers have started orphans their saved checks.
