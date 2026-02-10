# app/main.py
from fastapi import FastAPI
from app.core.cors import add_cors
from app.routers import dataset, lookup

def create_app() -> FastAPI:
    app = FastAPI(title="taxSun API")
    add_cors(app)
    #app.include_router(dataset.router, prefix="/process")
    #app.include_router(lookup.router, prefix="/lookup")
    app.include_router(dataset.router)
    app.include_router(lookup.router)
    return app

app = create_app()
