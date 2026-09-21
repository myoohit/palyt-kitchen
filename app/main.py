from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Palyt Kitchen")

app.mount("/", StaticFiles(directory="static", html=True), name="static")
