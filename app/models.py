"""
Data shapes for the app.

These models validate that incoming data LOOKS right (correct types,
non-negative quantities, a known unit). They do not decide business
rules like "what happens when stock runs below par" - that logic lives
in stock_service.py and menu_service.py, not here.
"""

from pydantic import BaseModel, Field, field_validator

# Only these units are supported for now. Kept small on purpose -
# the given data only uses weight and volume units.
ALLOWED_UNITS = {"g", "kg", "ml", "l"}


class Ingredient(BaseModel):
    name: str
    qty: float = Field(ge=0, description="Current quantity in stock")
    unit: str
    par: float = Field(ge=0, description="Minimum buffer level")

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Ingredient name cannot be blank")
        return value

    @field_validator("unit")
    @classmethod
    def unit_must_be_known(cls, value: str) -> str:
        if value not in ALLOWED_UNITS:
            raise ValueError(f"unit must be one of {sorted(ALLOWED_UNITS)}")
        return value


class IngredientUpdate(BaseModel):
    """
    Payload for editing an existing ingredient's quantity and/or par
    level. Both are optional so a caller can update just one without
    having to resend the other. Name and unit are not editable here -
    see stock_service.update_ingredient for why.
    """

    qty: float | None = Field(default=None, ge=0)
    par: float | None = Field(default=None, ge=0)


class RecipeIngredient(BaseModel):
    """One line in a recipe: how much of one ingredient a dish needs."""

    name: str
    qty: float = Field(gt=0, description="Amount used per portion")
    unit: str

    @field_validator("unit")
    @classmethod
    def unit_must_be_known(cls, value: str) -> str:
        if value not in ALLOWED_UNITS:
            raise ValueError(f"unit must be one of {sorted(ALLOWED_UNITS)}")
        return value


class Recipe(BaseModel):
    dish: str
    price: float = Field(ge=0)
    ingredients: list[RecipeIngredient]

class MenuItem(BaseModel):
    dish: str
    price: float
    available: bool


class MenuItem(BaseModel):
    dish: str
    price: float
    available: bool

class OrderRequest(BaseModel):
    dish: str