"""
app/main.py — Forced Enterprise Routing Setup
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.config import settings

def create_app() -> FastAPI:
    app = FastAPI(
        title="GradeOps Engine",
        version="1.0.0",
        docs_url="/docs"
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Force registration of our upgraded routers
    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health", include_in_schema=False)
    async def health():
        return {"status": "ok"}

    return app

app = create_app()