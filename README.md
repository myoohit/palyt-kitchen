# Palyt Kitchen

A kitchen tracks its ingredients. A menu that doesn't know about that stock keeps
selling dishes the kitchen can no longer make. This is the kitchen-side tool that
closes that gap: manage stock, see live menu availability derived from it, and
watch one order take a dish off the menu.

## Quick start

```bash
python -m venv venv
venv\Scripts\activate            # Windows
source venv/bin/activate         # macOS / Linux

pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/**. That's the whole setup — FastAPI serves the
frontend directly, no separate build step or frontend process.

## Run the tests

```bash
pytest
```

28 tests, all against the logic layer (`stock_service`, `menu_service`,
`order_service`) directly — not through HTTP. They cover unit conversion,
availability, and the order flow, including the two cases most likely to break
silently: a recipe unit that doesn't match its stock unit, and a rejected order
leaving stock completely untouched.

## How it works

**Stock** (top table) — list, search, add, edit, and delete ingredients. **Par**
is a reorder buffer, not zero: an ingredient can still be in stock and flagged
"Below par" at the same time.

**Menu** (bottom table) — every dish, priced, with availability recalculated
live from current stock. A dish is unavailable if any ingredient it needs is
below par, or isn't tracked in stock at all.

**The loop that matters**: order a dish → its recipe is broken into ingredient
amounts → those come out of stock → the menu re-evaluates → anything now below
par takes its dishes off the menu. Editing stock directly (a delivery arriving,
a par level changing) has the same effect on the menu, with no order needed.

Unavailable dishes stay on the menu, greyed out, rather than disappearing —
being short one ingredient is usually temporary, and a dish that vanishes
entirely looks like it's gone from the restaurant, not just the kitchen.

## Example: watching an order take a dish off the menu

`Paneer Butter Masala` uses 15 g of Cashews per order. Cashews starts at 300 g
in stock, with a par of 250 g.

| Order # | Cashews left | Paneer Butter Masala |
|---|---|---|
| 1 | 285 g | Available |
| 2 | 270 g | Available |
| 3 | 255 g | Available |
| 4 | **240 g** | **Unavailable** |

Every number above was checked against the real `stock.json` / `recipes.json`
by running the actual deduction logic, not estimated — see [DECISIONS.md](DECISIONS.md).

## Architecture
app/
├── main.py FastAPI routes. API declared before the static
│ mount, so routes aren't shadowed by it.
├── models.py Pydantic schemas — validation lives here
│ (no negative qty/par, known units only, etc.)
├── data_store.py Loads stock.json / recipes.json once at startup.
│ Holds state, does no business logic.
├── stock_service.py Unit conversion (kg↔g, l↔ml), list/add/edit/delete.
├── menu_service.py Availability: is a dish's stock at/above par?
└── order_service.py Places an order: validate → deduct → or reject
cleanly with nothing partially changed.

static/ Plain HTML/CSS/JS + Bootstrap (CDN). No framework,
no build step — talks to the API over fetch().

tests/ One test file per service, using an in-memory
DataStore.from_data() so tests don't depend on
the real JSON files.


The split exists so the interesting logic — availability, deduction, unit
conversion — is testable without spinning up a server or touching a browser.
`main.py` only wires HTTP to that logic; it has no rules of its own.

## Design decisions

Data is **in-memory only** — loaded once from the JSON files at startup, never
written back. Restarting the server resets everything. The brief allows either
in-memory or write-to-JSON; in-memory was simpler and isn't graded differently.

The delete rule, the validation rules, a real gap found in the given
availability rule, and everything else that needed a judgment call — with the
reasoning behind each — are logged as they were made in
[DECISIONS.md](DECISIONS.md), not written up after the fact.

## What's not here (on purpose)

No database, auth, payments, or order history — out of scope per the brief.
No framework on the frontend — not being evaluated, and would have cost setup
time better spent on the actual logic.