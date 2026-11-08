"""FastAPI entry point. Lifespan manages engine startup/shutdown."""
from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.serving.engine import LLMEngine
from src.serving.middleware import (
    APIKeyMiddleware,
    BodySizeLimitMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
)
from src.serving.routes import generate, health
from src.utils.config_parser import load_serving_config
from src.utils.logger import configure_logging, get_logger

configure_logging()
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = load_serving_config()
    eng = LLMEngine(cfg)
    model_path = os.getenv("MERGED_MODEL_PATH") or os.getenv("MODEL_ID", "")
    await eng.start(model_path)
    app.state.engine = eng
    try:
        yield
    finally:
        await eng.stop()


def create_app() -> FastAPI:
    cfg = load_serving_config()
    app = FastAPI(
        title="LLM-Forge",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if os.getenv("ENV", "prod") != "prod" else None,
        redoc_url=None,
        openapi_url="/openapi.json" if os.getenv("ENV", "prod") != "prod" else None,
    )

    origins = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=False,
            allow_methods=["POST", "GET"],
            allow_headers=["Authorization", "Content-Type"],
        )

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(BodySizeLimitMiddleware, max_bytes=cfg.security.max_request_bytes)
    app.add_middleware(RateLimitMiddleware, limit_per_minute=cfg.security.rate_limit_per_minute)
    app.add_middleware(APIKeyMiddleware)

    app.include_router(health.router)
    app.include_router(generate.router)

    return app


app = create_app()
