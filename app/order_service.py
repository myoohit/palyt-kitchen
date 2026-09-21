"""
Business logic for placing an order: looks up a dish's recipe, checks
it's currently available, and deducts its ingredients from stock.

Deduction goes through stock_service.to_base_quantity() /
from_base_quantity() because a recipe's ingredient can be written in a
different unit than the stock entry it draws from (e.g. a recipe needs
200 g of something that's tracked in kg in stock.json).

Stays independent of FastAPI, same as stock_service and menu_service.
"""

from app.data_store import DataStore
from app.menu_service import is_dish_available
from app import stock_service


class DishNotFoundError(Exception):
    """Raised when ordering a dish that isn't in recipes.json."""


class DishUnavailableError(Exception):
    """Raised when ordering a dish that's currently unavailable."""


class InsufficientStockError(Exception):
    """
    Raised if deducting the order would push an ingredient below zero.

    This is a separate case from "unavailable": is_dish_available() only
    checks that stock is at or above par, not that there's enough left
    for one specific order. Par is a reorder buffer, not a guarantee -
    an ingredient can sit right at par and still not have enough for a
    dish that needs more than that per order. See DECISIONS.md.
    """


def place_order(store: DataStore, dish_name: str):
    """
    Places one order for the given dish: validates it exists and is
    available, then deducts its recipe's ingredients from stock.

    All deductions are worked out first and only written to the store
    if every one of them is valid, so a failure partway through never
    leaves stock partially deducted.
    """
    recipe = next((r for r in store.list_recipes() if r.dish == dish_name), None)
    if recipe is None:
        raise DishNotFoundError(f"'{dish_name}' is not on the menu")

    if not is_dish_available(store, recipe):
        raise DishUnavailableError(f"'{dish_name}' is currently unavailable")

    updates = []
    for line in recipe.ingredients:
        ingredient = store.get_ingredient(line.name)
        deduction = stock_service.from_base_quantity(
            stock_service.to_base_quantity(line.qty, line.unit),
            ingredient.unit,
        )
        new_qty = ingredient.qty - deduction
        if new_qty < 0:
            raise InsufficientStockError(
                f"Not enough '{ingredient.name}' in stock for '{dish_name}'"
            )
        updates.append((ingredient.name, new_qty))

    for name, new_qty in updates:
        stock_service.update_ingredient(store, name, qty=new_qty)

    return recipe