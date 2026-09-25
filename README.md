# Travel Field Guide

A reusable, offline-first mobile "field guide" app for **any** trip — plus a
Claude skill that builds one for you from a placeholder.

It's a single `index.html` (no dependencies, no server) with five tabs:

- **Today**: a live departure board. It counts down before the trip, opens to the current day during it, and shows the timetable and heads-ups.
- **Days**: every day's hour-by-hour plan, a numbered walking tour (each stop opens in Google Maps, with a "Seen" toggle), where to eat, local foods, tips and private notes.
- **Places**: hotels (tap to navigate or call) and a card for each city with its sights, restaurants and local specialties.
- **Lists**: packing checklists and per-person shopping lists, saved on the device.
- **Info**: emergency numbers, hospitals and embassy, money tips, booked tours and transfers, transport tables, the shared photo album and a trip-log export.

The accent color changes with each leg of the trip (country or region), so travelers can see which leg they're on.

**[`index.html`](index.html)** in this repo is the placeholder demo built from
[`trip.json`](trip.json). Every `[bracketed]` value is a slot to fill in.

## Build one for your trip

```bash
cp skill/travel-field-guide/assets/trip.example.json my-trip.json
# fill in every [placeholder]; delete sections you don't need (they hide automatically)
python3 skill/travel-field-guide/scripts/build.py my-trip.json -o index.html
node skill/travel-field-guide/scripts/validate.js index.html   # optional; needs Playwright
```

`build.py` checks the data before writing anything. Days must be numbered 1..N, each date must match its weekday, and every day and city must point to a real leg. It warns while `[placeholder]` text remains. To change a trip that's already built, pull its data back out, edit, and rebuild:

```bash
python3 skill/travel-field-guide/scripts/build.py --extract index.html -o trip.json
```

The complete field reference is [`skill/travel-field-guide/references/data-model.md`](skill/travel-field-guide/references/data-model.md).

## Or let Claude build it: the skill

[`skill/travel-field-guide/`](skill/travel-field-guide/) is a self-contained
Claude skill (`SKILL.md` + template + placeholder trip + build and validate
scripts + references). Give Claude your itinerary and ask for "a field guide
app for our trip". It copies the placeholder, fills it in, checks facts,
builds and validates the app, and hands you `index.html`.

To install it, zip the folder and upload it under **claude.ai → Settings → Capabilities → Skills**. For Claude Code, copy it into `~/.claude/skills/`:

```bash
cd skill && zip -r travel-field-guide.zip travel-field-guide
```

## Layout

```
index.html, trip.json            placeholder demo (GitHub Pages serves index.html)
skill/travel-field-guide/
  SKILL.md                       how Claude builds/edits a trip app
  assets/template.html           the app engine — trip-agnostic, one DATA slot
  assets/trip.example.json       the placeholder trip to copy
  scripts/build.py               validate + build + extract
  scripts/validate.js            headless click-through smoke test
  references/                    data model, design system, editing workflow
```

## Share it with your group

1. Put `index.html` (and your `trip.json`) in a GitHub repo, then go to **Settings → Pages → Deploy from branch `main` / root**.
2. Share `https://<user>.github.io/<repo>/`, ideally as a QR code in the group chat.
3. Each traveler opens it once and chooses **Add to Home Screen**. After that it works offline.

Checkmarks, notes and "Seen" toggles are saved on each device and aren't shared between travelers. Each trip keeps its saved data separate (`meta.storageId`), so several trips hosted under one `github.io` account won't mix up each other's checkmarks.
