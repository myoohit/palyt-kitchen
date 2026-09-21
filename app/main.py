"""
Palyt Kitchen - entry point.

Defines the API routes and serves the static frontend. API routes are
declared before the static mount, so they take priority over it -
otherwise the catch-all static file server would swallow their paths.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.data_store import store
from app import stock_service

app = FastAPI(title="Palyt Kitchen")


@app.get("/api/ingredients")
def get_ingredients():
    """Returns the current stock list."""
    return stock_service.list_ingredients(store)


# Serves everything in /static, including index.html at the root path.
# html=True makes "/" resolve to index.html automatically.
# Mounted last so it doesn't shadow the API routes above.
app.mount("/", StaticFiles(directory="static", html=True), name="static")