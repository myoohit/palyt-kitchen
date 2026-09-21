"""
Business logic for the menu: works out whether each dish is currently
available, based on its recipe's ingredients.

A dish is UNAVAILABLE if any one of its ingredients:
- isn't tracked in stock at all (e.g. Cumin Seeds, Refined Flour), or
- has a current quantity below its par level.

Note: this check compares an ingredient's qty and par directly, with no
unit conversion needed - both are always stored in the same unit for a
given ingredient. Unit conversion (to_base_quantity) only becomes
necessary when deducting a recipe's quantities from stock, since a
recipe line can be in a different unit than the stock entry it draws
from (e.g. recipe needs 200 g, stock is tracked in kg).

Like stock_service, this stays independent of FastAPI so it can be
tested directly against a DataStore.
"""

from app.data_store import DataStore
from app.models import MenuItem, Recipe


def is_dish_available(store: DataStore, recipe: Recipe) -> bool:
    """
    Returns True only if every ingredient the recipe needs exists in
    stock and its current quantity is at or above its par level.
    """
    for line in recipe.ingredients:
        ingredient = store.get_ingredient(line.name)
        if ingredient is None:
            return False
        if ingredient.qty < ingredient.par:
            return False
    return True


def get_menu(store: DataStore) -> list[MenuItem]:
    """Returns every dish with its price and current availability."""
    return [
        MenuItem(
            dish=recipe.dish,
            price=recipe.price,
            available=is_dish_available(store, recipe),
        )
        for recipe in store.list_recipes()
    ]