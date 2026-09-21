"""
Palyt Kitchen - entry point.

Defines the API routes and serves the static frontend. API routes are
declared before the static mount, so they take priority over it -
otherwise the catch-all static file server would swallow their paths.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles

from app.data_store import store
from app.models import IngredientUpdate
from app import stock_service

app = FastAPI(title="Palyt Kitchen")


@app.get("/api/ingredients")
def get_ingredients():
    """Returns the current stock list."""
    return stock_service.list_ingredients(store)


@app.put("/api/ingredients/{name}")
def edit_ingredient(name: str, payload: IngredientUpdate):
    """Updates an ingredient's quantity and/or par level."""
    try:
        return stock_service.update_ingredient(
            store, name, qty=payload.qty, par=payload.par
        )
    except stock_service.IngredientNotFoundError:
        raise HTTPException(status_code=404, detail=f"'{name}' not found")


# Serves everything in /static, including index.html at the root path.
# html=True makes "/" resolve to index.html automatically.
# Mounted last so it doesn't shadow the API routes above.
app.mount("/", StaticFiles(directory="static", html=True), name="static")