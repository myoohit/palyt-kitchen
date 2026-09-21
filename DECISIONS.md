# Decisions

Judgment calls made while building this, and why. Filled in as each one is
actually decided (not upfront), so this reflects real reasoning rather than
guesses made before touching the data.



## Decided

- **Unit conversion**: comparisons and deductions are done in a common
  base unit (grams for weight, ml for volume) via
  `stock_service.to_base_quantity()` / `from_base_quantity()`. Display
  still shows whatever unit the ingredient's stock record uses -
  conversion only happens internally when comparing or subtracting
  amounts.
- **Ingredients missing from stock** (Cumin Seeds, Refined Flour - used
  by Veg Pulao, Jeera Rice, Butter Naan but not present in stock.json):
  a dish needing one of these is treated as unavailable, rather than
  assuming an untracked ingredient is infinitely available.
- **Storage**: data lives in memory only, loaded once from stock.json /
  recipes.json at startup. Add/edit/delete/order all change the
  in-memory copy, never the JSON files - restarting the server resets
  everything back to the original data. The brief allows either
  in-memory or write-to-JSON; in-memory was simpler and not graded
  differently, so that's what this uses.
- **Deleting an ingredient a recipe still needs** (e.g. Cashews, used
  by 2 dishes) is blocked, naming the affected dishes in the error.
  Silently deleting it would make those dishes permanently unavailable
  with no visible reason why, which is worse than refusing the delete
  up front. Deleting an ingredient no recipe uses (e.g. Bay Leaves) is
  allowed freely.
- **Availability vs orderability**: `is_dish_available()` only checks
  that stock is at or above par - it does NOT guarantee there's enough
  for one specific order. Par is a reorder buffer, not a hard
  reservation. An ingredient sitting exactly at par can still be short
  for a dish needing more than that per order. This is the case where
  the "below par" rule can misbehave: a dish can show as Available and
  still get rejected at order time. Handled with a separate
  `InsufficientStockError` in order_service.py, distinct from
  `DishUnavailableError` - see test_place_order_raises_insufficient_stock_without_partial_deduction.