import pytest

from app.data_store import DataStore
from app.models import Ingredient, Recipe, RecipeIngredient
from app import order_service


def make_store():
    ingredients = [
        Ingredient(name="Chicken", qty=500, unit="g", par=200),
        Ingredient(name="Rice", qty=1000, unit="g", par=500),
        Ingredient(name="Paneer", qty=1.4, unit="kg", par=0.5),  # for unit mismatch
        Ingredient(name="Butter", qty=50, unit="g", par=100),  # below par
    ]
    recipes = [
        Recipe(
            dish="Chicken Rice",
            price=250,
            ingredients=[
                RecipeIngredient(name="Chicken", qty=200, unit="g"),
                RecipeIngredient(name="Rice", qty=150, unit="g"),
            ],
        ),
        Recipe(
            dish="Paneer Rice",
            price=200,
            ingredients=[
                # recipe unit (g) differs from stock unit (kg) on purpose
                RecipeIngredient(name="Paneer", qty=200, unit="g"),
                RecipeIngredient(name="Rice", qty=150, unit="g"),
            ],
        ),
        Recipe(
            dish="Buttered Rice",
            price=120,
            ingredients=[
                RecipeIngredient(name="Rice", qty=150, unit="g"),
                RecipeIngredient(name="Butter", qty=20, unit="g"),
            ],
        ),
        Recipe(
            dish="Veg Pulao",
            price=180,
            ingredients=[
                RecipeIngredient(name="Rice", qty=150, unit="g"),
                RecipeIngredient(name="Cumin Seeds", qty=5, unit="g"),  # untracked
            ],
        ),
    ]
    return DataStore.from_data(ingredients, recipes)


def test_place_order_deducts_ingredients_in_matching_units():
    store = make_store()
    order_service.place_order(store, "Chicken Rice")

    assert store.get_ingredient("Chicken").qty == 300  # 500 - 200
    assert store.get_ingredient("Rice").qty == 850  # 1000 - 150


def test_place_order_converts_units_before_deducting():
    store = make_store()
    order_service.place_order(store, "Paneer Rice")

    # Paneer is tracked in kg; recipe needs 200 g -> 0.2 kg deducted.
    assert store.get_ingredient("Paneer").qty == pytest.approx(1.2)


def test_place_order_raises_for_unknown_dish():
    store = make_store()
    with pytest.raises(order_service.DishNotFoundError):
        order_service.place_order(store, "Nonexistent Dish")


def test_place_order_raises_for_unavailable_dish_due_to_below_par_ingredient():
    store = make_store()
    with pytest.raises(order_service.DishUnavailableError):
        order_service.place_order(store, "Buttered Rice")
    # nothing should be deducted from a rejected order
    assert store.get_ingredient("Rice").qty == 1000


def test_place_order_raises_for_dish_needing_untracked_ingredient():
    store = make_store()
    with pytest.raises(order_service.DishUnavailableError):
        order_service.place_order(store, "Veg Pulao")


def test_place_order_raises_insufficient_stock_without_partial_deduction():
    ingredients = [
        Ingredient(name="Saffron", qty=5, unit="g", par=2),
        Ingredient(name="Basmati Rice", qty=1000, unit="g", par=500),
    ]
    recipes = [
        Recipe(
            dish="Saffron Rice",
            price=300,
            ingredients=[
                # needs more saffron than is currently in stock, even
                # though 5g is still above the 2g par
                RecipeIngredient(name="Saffron", qty=10, unit="g"),
                RecipeIngredient(name="Basmati Rice", qty=150, unit="g"),
            ],
        )
    ]
    store = DataStore.from_data(ingredients, recipes)

    with pytest.raises(order_service.InsufficientStockError):
        order_service.place_order(store, "Saffron Rice")

    # Rice must be untouched too - the whole order rolls back, not just
    # the ingredient that failed.
    assert store.get_ingredient("Basmati Rice").qty == 1000
    assert store.get_ingredient("Saffron").qty == 5