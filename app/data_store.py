"""
Loads stock.json and recipes.json into memory and holds the current state.

This class deliberately does nothing clever - it does not decide
availability, does not convert units, and does not validate business
rules. It only loads data and gives controlled read/write access to it.
That keeps stock_service.py and menu_service.py easy to test, since they
can be handed a DataStore (or a fake one) without touching real files.
"""

import json
from pathlib import Path

from app.models import Ingredient, Recipe

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class DataStore:
    def __init__(
        self,
        stock_path: Path = DATA_DIR / "stock.json",
        recipes_path: Path = DATA_DIR / "recipes.json",
    ):
        self._stock_path = stock_path
        self._recipes_path = recipes_path
        self.ingredients: dict[str, Ingredient] = {}
        self.recipes: list[Recipe] = []
        self._load()

    def _load(self) -> None:
        with open(self._stock_path) as f:
            raw_stock = json.load(f)
        self.ingredients = {
            item["name"]: Ingredient(**item) for item in raw_stock
        }

        with open(self._recipes_path) as f:
            raw_recipes = json.load(f)
        self.recipes = [Recipe(**item) for item in raw_recipes]

    # --- Ingredients ---

    def list_ingredients(self) -> list[Ingredient]:
        return list(self.ingredients.values())

    def get_ingredient(self, name: str) -> Ingredient | None:
        return self.ingredients.get(name)

    def upsert_ingredient(self, ingredient: Ingredient) -> None:
        """Add a new ingredient, or overwrite an existing one with the same name."""
        self.ingredients[ingredient.name] = ingredient

    def delete_ingredient(self, name: str) -> bool:
        """Returns True if something was deleted, False if the name didn't exist."""
        if name in self.ingredients:
            del self.ingredients[name]
            return True
        return False

    # --- Recipes ---

    def list_recipes(self) -> list[Recipe]:
        return self.recipes

    # --- Testing helper ---

    @classmethod
    def from_data(cls, ingredients: list[Ingredient], recipes: list[Recipe]) -> "DataStore":
        """
        Builds a DataStore directly from already-loaded data, skipping the
        file reads. Used by tests so they don't depend on the real JSON
        files, or break if stock.json changes later.
        """
        store = cls.__new__(cls)
        store.ingredients = {i.name: i for i in ingredients}
        store.recipes = recipes
        return store
# A single shared instance used by the whole app while it's running.
store = DataStore()