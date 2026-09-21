"""
Business logic for stock: unit conversion and reading the ingredient list.

This module works directly with DataStore and the Ingredient model, and
doesn't know anything about FastAPI or HTTP - that's what lets us test it
without spinning up a server. Editing/adding/deleting ingredients will be
added here in a later commit.
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