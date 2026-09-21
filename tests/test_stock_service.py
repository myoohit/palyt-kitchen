"""
Tests for stock_service.

These use DataStore.from_data() instead of the real JSON files, so they
keep passing even if stock.json or recipes.json change later.
"""

import pytest

from app.data_store import DataStore
from app.models import Ingredient
from app import stock_service


def make_test_store() -> DataStore:
    ingredients = [
        Ingredient(name="Paneer", qty=1.4, unit="kg", par=0.5),
        Ingredient(name="Cashews", qty=300, unit="g", par=250),
    ]
    return DataStore.from_data(ingredients=ingredients, recipes=[])


def test_to_base_quantity_converts_kg_to_grams():
    assert stock_service.to_base_quantity(1.4, "kg") == 1400


def test_to_base_quantity_converts_litres_to_ml():
    assert stock_service.to_base_quantity(0.9, "l") == 900


def test_to_base_quantity_leaves_base_units_unchanged():
    assert stock_service.to_base_quantity(300, "g") == 300
    assert stock_service.to_base_quantity(900, "ml") == 900


def test_to_base_quantity_rejects_unknown_unit():
    with pytest.raises(ValueError):
        stock_service.to_base_quantity(5, "cups")


def test_list_ingredients_returns_everything_in_store():
    store = make_test_store()
    names = {i.name for i in stock_service.list_ingredients(store)}
    assert names == {"Paneer", "Cashews"}