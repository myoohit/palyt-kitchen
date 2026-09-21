"""
Business logic for stock: unit conversion, reading the ingredient list,
and editing an existing ingredient's quantity or par level.

This module works directly with DataStore and the Ingredient model, and
doesn't know anything about FastAPI or HTTP - that's what lets us test it
without spinning up a server. Add/delete will be added here in a later
commit.
"""

from app.data_store import DataStore
from app.models import Ingredient

# How many "base units" one of each unit is worth.
# Weight is normalized to grams, volume to millilitres, so that a
# quantity in kg and one in g can be compared or subtracted safely.
_CONVERSION_TO_BASE = {
    "g": 1,
    "kg": 1000,
    "ml": 1,
    "l": 1000,
}


def to_base_quantity(qty: float, unit: str) -> float:
    """
    Converts a quantity to its base unit: grams for weight, ml for volume.

    Example: to_base_quantity(1.4, "kg") -> 1400
    """
    if unit not in _CONVERSION_TO_BASE:
        raise ValueError(f"Unknown unit: {unit}")
    return qty * _CONVERSION_TO_BASE[unit]

def from_base_quantity(base_qty: float, unit: str) -> float:
    """
    The inverse of to_base_quantity: converts a base-unit amount (grams
    or ml) into the given unit. Used when a recipe line's unit differs
    from the stock entry it's deducted from - e.g. a recipe needs 200 g
    but the stock entry for that ingredient is tracked in kg, so the
    deduction has to be expressed in kg before it's subtracted.
    """
    if unit not in _CONVERSION_TO_BASE:
        raise ValueError(f"Unknown unit: {unit}")
    return base_qty / _CONVERSION_TO_BASE[unit]


def list_ingredients(store: DataStore) -> list[Ingredient]:
    """Returns every ingredient currently in stock."""
    return store.list_ingredients()


class IngredientNotFoundError(Exception):
    """Raised when trying to update or delete an ingredient that doesn't exist."""

class IngredientAlreadyExistsError(Exception):
    """Raised when adding an ingredient whose name is already in stock."""


class IngredientInUseError(Exception):
    """Raised when deleting an ingredient that's still used by a recipe."""


def add_ingredient(store: DataStore, ingredient: Ingredient) -> Ingredient:
    """
    Adds a new ingredient. Rejects if the name already exists - editing
    an existing one should go through update_ingredient instead, so add
    and edit don't silently overlap.

    Comparison is case-insensitive, so "Cashews" and "cashews" can't
    become two separate stock entries - the given data has no such
    duplicates, but nothing stops someone from typing one in.
    """
    duplicate = any(
        existing.name.lower() == ingredient.name.lower()
        for existing in store.list_ingredients()
    )
    if duplicate:
        raise IngredientAlreadyExistsError(f"'{ingredient.name}' already exists")
    store.upsert_ingredient(ingredient)
    return ingredient

def delete_ingredient(store: DataStore, name: str) -> None:
    """
    Deletes an ingredient, unless some recipe still needs it. Deleting
    it out from under a recipe would silently make that dish permanently
    unavailable with no clear reason why - so this blocks the delete
    instead and names which dishes are affected.
    """
    if store.get_ingredient(name) is None:
        raise IngredientNotFoundError(f"'{name}' does not exist")

    affected = [
        recipe.dish
        for recipe in store.list_recipes()
        if any(line.name == name for line in recipe.ingredients)
    ]
    if affected:
        raise IngredientInUseError(
            f"Can't delete '{name}' - used by {', '.join(affected)}"
        )

    store.delete_ingredient(name)


def update_ingredient(
    store: DataStore,
    name: str,
    qty: float | None = None,
    par: float | None = None,
) -> Ingredient:
    """
    Updates qty and/or par for an existing ingredient. Whichever field is
    left as None keeps its current value.

    Unit and name aren't editable through this function - changing what
    unit an ingredient is measured in is a bigger decision (it would mean
    re-checking every recipe that references it) than a routine restock
    or par change should trigger.

    Rebuilding the Ingredient from scratch (rather than mutating fields
    directly) means it goes through the same validation as creating a
    new one, so a negative qty or par is rejected here too.
    """
    existing = store.get_ingredient(name)
    if existing is None:
        raise IngredientNotFoundError(f"'{name}' does not exist")

    updated = Ingredient(
        name=existing.name,
        qty=qty if qty is not None else existing.qty,
        unit=existing.unit,
        par=par if par is not None else existing.par,
    )
    store.upsert_ingredient(updated)
    return updated