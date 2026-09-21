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


def list_ingredients(store: DataStore) -> list[Ingredient]:
    """Returns every ingredient currently in stock."""
    return store.list_ingredients()


class IngredientNotFoundError(Exception):
    """Raised when trying to update or delete an ingredient that doesn't exist."""


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