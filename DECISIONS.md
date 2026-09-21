# Decisions

Judgment calls made while building this, and why. Filled in as each one is
actually decided (not upfront), so this reflects real reasoning rather than
guesses made before touching the data.

## Open questions to resolve

- Deleting an ingredient that a recipe still depends on, vs. one that no
  recipe uses (e.g. Cashews vs Bay Leaves). What happens in each case?
- Any case where the "unavailable if any ingredient is below par" rule
  produces a bad or surprising result.

## Decided

- **Unit conversion**: comparisons and deductions will be done in a common
  base unit (grams for weight, ml for volume), converting kg/l on the way
  in. Display will still show whatever unit the ingredient's stock record
  uses. Not yet implemented - will land with stock_service.py.
- **Ingredients missing from stock** (Cumin Seeds, Refined Flour - used by
  Veg Pulao, Jeera Rice, Butter Naan but not present in stock.json): a dish
  needing one of these is treated as unavailable, rather than assuming an
  untracked ingredient is infinitely available. Not yet implemented - will
  land with menu_service.py.