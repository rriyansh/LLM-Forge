"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.serving.middleware import AuthMiddleware, RateLimitMiddleware, RequestLoggingMiddleware
from src.serving.routes.generate import router as generate_router


def create_app() -> FastAPI:
    app = FastAPI(title="LLM-Forge Serving", version="0.1.0")

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(AuthMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(generate_router, prefix="/v1")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
