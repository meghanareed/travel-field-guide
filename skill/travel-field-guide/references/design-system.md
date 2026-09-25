# Design system — "Continental Pullman" night-train field guide

The look is a warm, printed night-train field guide: ticket-stock paper, deep
midnight-teal chrome, brass accents, and a per-country accent that shifts as the
trip moves between legs. The look is trip-agnostic — it suits any destination. Keep this identity when editing; don't reach for a
generic UI kit. Everything is defined in the `<style>` block of the app.

## Core tokens (CSS variables)

- `--paper: #FAF6EE` (ticket stock), `--paper-2` (slightly deeper paper)
- `--ink` (near-black warm text), `--ink-soft` (secondary text), `--line` (hairline), `--card`
- `--night: #0E2A33` chrome (top bar, nav) — also the `theme-color` meta
- `--brass: #B8893E` / `--brass-bright: #C99A4A` — pricetags, small accents
- `--accent` — **set at runtime per view** via `setAccent(color)`

## Per-leg accent colors (`DATA.legs`)

Each trip leg gets an accent; the current day's leg sets `--accent`, colors the
day card stripe, the timetable dots, stop numbers and buttons. Legs are defined
in the trip JSON (`legs: {key:{name,flag,color}}`) — the engine has no
hard-coded countries. `transit` is the neutral `#7A6A52`.

Tested palette — all read well on the paper and carry white text:

| color | hex | good for |
|---|---|---|
| gold | `#C8941E` | sunny / Mediterranean / Belgium-style legs |
| slate blue | `#3E6B8C` | coastal, Nordic, lakes |
| brick red | `#A8423C` | France, Spain, Japan, deserts |
| forest green | `#2F6B4F` | Alps, Ireland, Portugal, national parks |
| plum | `#6B4A7A` | cities at night, Prague, Vienna |
| teal | `#2E7C7A` | islands, Greece, Croatia |
| rust | `#B0612E` | Morocco, Southwest US, autumn |
| transit | `#7A6A52` | travel days, overview screens |

Keep adjacent legs visibly different. Flags: a country flag emoji, or a
regional symbol (🏔️ 🏝️ 🍷) when legs are regions inside one country.

`setLegPill({name, flag})` renders the pill in the top bar; overview screens
(Days list, Info, Lists) use transit, Places uses the first leg, Shopping uses
the list's own `accent`.

## Typography

System font stacks only — **no web fonts** (offline reliability):
- serif for display/headlines, sans for body, monospace (`--mono`) for times,
  eyebrows, pricetags, and the departure board.

## Signature components

- **Departure board**: the day `schedule` renders as a vertical timetable with
  monospaced times on a track — the app's signature element. Keep it for
  schedules.
- **`.section-head`**: eyebrow (mono, uppercase) + `.h-section` title + `.sub`.
- **`.card.pad`**: the standard rounded paper card.
- **`.acc` / `<details>`**: accordions (Places cities, Packing lists).
- **`.check` / `.box` / `.lbl`**: a checkbox row (packing + shopping). `.check.on`
  fills the box with `--accent`.
- **`.seg`**: segmented switcher (Packing/Shopping, and the person switcher). It
  wraps (`flex-wrap`) so 3–4 options fit on a phone.
- **`.stop` / `.num` / `.maplink`**: walking-tour stop with numbered badge and
  "📍 Open in Maps". `.seentog` is the per-stop Seen pill.
- **`.leg` / `.leg-ic`**: transit connector row (dashed train icon, tinted).
- **`.tier-head`**: mono accent sub-header inside shopping lists.
- **`.buydetails`**: the expandable price/does/shade panel; shown via
  `.check.open + .buydetails`.
- **`.pricetag`**: mono brass, used for counts and shopping prices.

## Layout rules

- Mobile-first, ~390px design width; a phone shows ~6–8 lines at once.
- Minimal formatting; let the paper + accents carry the style.
- Bottom nav: keep to 5 tabs so labels don't wrap. Add capability via a
  segmented sub-switch, not more tabs.
- Respect `prefers-reduced-motion` (already handled).
- Every screen sets an accent so the top bar/leg pill stays coherent; checklist
  views use the transit neutral for Packing and the list's own accent for
  Shopping.
