import pytest

from app.data_store import DataStore
from app.models import Ingredient, Recipe, RecipeIngredient
from app import stock_service


def make_store_with_recipes():
    ingredients = [
        Ingredient(name="Cashews", qty=300, unit="g", par=250),
        Ingredient(name="Bay Leaves", qty=40, unit="g", par=10),
    ]
    recipes = [
        Recipe(
            dish="Kaju Curry",
            price=280,
            ingredients=[RecipeIngredient(name="Cashews", qty=50, unit="g")],
        ),
        Recipe(
            dish="Kaju Pulao",
            price=220,
            ingredients=[RecipeIngredient(name="Cashews", qty=30, unit="g")],
        ),
    ]
    return DataStore.from_data(ingredients, recipes)


def test_add_ingredient_succeeds_for_new_name():
    store = make_store_with_recipes()
    new_item = Ingredient(name="Turmeric", qty=100, unit="g", par=20)
    stock_service.add_ingredient(store, new_item)
    assert store.get_ingredient("Turmeric").qty == 100


def test_add_ingredient_rejects_duplicate_name():
    store = make_store_with_recipes()
    duplicate = Ingredient(name="Cashews", qty=999, unit="g", par=1)
    with pytest.raises(stock_service.IngredientAlreadyExistsError):
        stock_service.add_ingredient(store, duplicate)

def test_add_ingredient_rejects_duplicate_name_case_insensitive():
    store = make_store_with_recipes()
    duplicate = Ingredient(name="cashews", qty=999, unit="g", par=1)
    with pytest.raises(stock_service.IngredientAlreadyExistsError):
        stock_service.add_ingredient(store, duplicate)


def test_delete_ingredient_succeeds_when_unreferenced():
    store = make_store_with_recipes()
    stock_service.delete_ingredient(store, "Bay Leaves")
    assert store.get_ingredient("Bay Leaves") is None


def test_delete_ingredient_blocked_when_referenced_by_recipes():
    store = make_store_with_recipes()
    with pytest.raises(stock_service.IngredientInUseError) as excinfo:
        stock_service.delete_ingredient(store, "Cashews")

    # error should name the affected dishes, not just say "in use"
    assert "Kaju Curry" in str(excinfo.value)
    assert "Kaju Pulao" in str(excinfo.value)
    # and the ingredient must still be there - nothing removed
    assert store.get_ingredient("Cashews") is not None


def test_delete_ingredient_raises_for_unknown_name():
    store = make_store_with_recipes()
    with pytest.raises(stock_service.IngredientNotFoundError):
        stock_service.delete_ingredient(store, "Nonexistent")