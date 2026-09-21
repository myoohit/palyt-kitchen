# Decisions

Judgment calls made while building this, and why. Filled in as each one is
actually decided (not upfront), so this reflects real reasoning rather than
guesses made before touching the data.

## Open questions to resolve

- Unit conversion: stock and recipes sometimes use different units for the
  same ingredient (e.g. kg vs g). How is this normalized before comparing
  or deducting?
- Ingredients in a recipe with no matching stock record (e.g. Cumin Seeds,
  Refined Flour are used in recipes but not present in stock.json). What
  should availability do for a dish that needs one of these?
- Deleting an ingredient that a recipe still depends on, vs. one that no
  recipe uses (e.g. Cashews vs Bay Leaves). What happens in each case?
- Any case where the "unavailable if any ingredient is below par" rule
  produces a bad or surprising result.

## Decided

(To be filled in as we build each part.)
