# app/main.py
from fastapi import FastAPI
from app.core.cors import add_cors
from app.routers import dataset, lookup

def create_app() -> FastAPI:
    app = FastAPI(title="taxSun API")
    add_cors(app)

    @app.get("/")
    def root():
        return {"status": "ok", "message": "taxSun backend alive"}

    @app.get("/health")
    def health():
        return {"healthy": True}

    app.include_router(dataset.router)
    app.include_router(lookup.router)

    return app

app = create_app()
