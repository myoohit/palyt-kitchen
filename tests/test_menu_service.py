from app.data_store import DataStore
from app.menu_service import get_menu, is_dish_available
from app.models import Ingredient, Recipe, RecipeIngredient


def make_store():
    ingredients = [
        Ingredient(name="Chicken", qty=500, unit="g", par=200),
        Ingredient(name="Rice", qty=1000, unit="g", par=500),
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


def test_dish_available_when_all_ingredients_at_or_above_par():
    store = make_store()
    recipe = next(r for r in store.list_recipes() if r.dish == "Chicken Rice")
    assert is_dish_available(store, recipe) is True


def test_dish_unavailable_when_an_ingredient_is_below_par():
    store = make_store()
    recipe = next(r for r in store.list_recipes() if r.dish == "Buttered Rice")
    assert is_dish_available(store, recipe) is False


def test_dish_unavailable_when_an_ingredient_is_untracked():
    store = make_store()
    recipe = next(r for r in store.list_recipes() if r.dish == "Veg Pulao")
    assert is_dish_available(store, recipe) is False


def test_dish_available_when_ingredient_qty_exactly_equals_par():
    # Par is a buffer, not a hard floor - being exactly at par should
    # still count as available, only going below it should not.
    ingredients = [Ingredient(name="Salt", qty=100, unit="g", par=100)]
    recipes = [
        Recipe(dish="Salted Thing", price=50, ingredients=[
            RecipeIngredient(name="Salt", qty=10, unit="g"),
        ])
    ]
    store = DataStore.from_data(ingredients, recipes)
    assert is_dish_available(store, recipes[0]) is True


def test_get_menu_returns_one_item_per_recipe_with_correct_availability():
    store = make_store()
    menu = get_menu(store)
    by_dish = {item.dish: item for item in menu}

    assert len(menu) == 3
    assert by_dish["Chicken Rice"].available is True
    assert by_dish["Chicken Rice"].price == 250
    assert by_dish["Buttered Rice"].available is False
    assert by_dish["Veg Pulao"].available is False


def test_get_menu_on_empty_recipes_returns_empty_list():
    store = DataStore.from_data([], [])
    assert get_menu(store) == []