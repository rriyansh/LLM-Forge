"""FastAPI application factory with hardened middleware + lifespan."""
from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src import __version__
from src.db.session import init_db
from src.models.warmup import warmup
from src.serving.cache import SemanticCache
from src.serving.engine import LLMEngine
from src.serving.middleware import build_middleware_stack
from src.serving.routes import admin, auth, chat, generate, health, metrics, models
from src.utils.config_parser import get_env, get_env_bool, load_serving_config
from src.utils.exceptions import LLMForgeError
from src.utils.logger import configure_logging, get_logger
from src.utils.tracing import init_tracing, instrument_fastapi

configure_logging()
log = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = load_serving_config()
    init_tracing()

    app.state.cache = SemanticCache()
    app.state.request_timeout = cfg.security.request_timeout_seconds

    engine = LLMEngine(cfg)
    model_path = get_env("MERGED_MODEL_PATH", "") or get_env("MODEL_ID", required=True)
    await engine.start(model_path)
    app.state.engine = engine

    if get_env_bool("MODEL_WARMUP_ENABLED", True):
        await warmup(engine, rounds=1)

    await init_db()
    log.info("app_ready", version=__version__)
    try:
        yield
    finally:
        await engine.stop()
        log.info("app_shutdown")


def create_app() -> FastAPI:
    cfg = load_serving_config()
    is_prod = get_env("ENV", "prod") == "prod"

    app = FastAPI(
        title="LLM-Forge",
        version=__version__,
        lifespan=lifespan,
        docs_url=None if is_prod else "/docs",
        redoc_url=None,
        openapi_url=None if is_prod else "/openapi.json",
        default_response_class=JSONResponse,
    )

    # CORS
    origins = [o.strip() for o in get_env("ALLOWED_ORIGINS", "").split(",") if o.strip()]
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=False,
            allow_methods=["GET", "POST"],
            allow_headers=["Authorization", "Content-Type", "X-API-Key", "X-Request-ID"],
            max_age=600,
        )

    # Security stack
    build_middleware_stack(app, allowlist=get_env("IP_ALLOWLIST", ""))

    # Exception handlers
    @app.exception_handler(LLMForgeError)
    async def _handle_llmforge(request: Request, exc: LLMForgeError) -> JSONResponse:
        log.info("app_error", code=exc.error_code, msg=exc.message)
        return JSONResponse(
            {"error": {"code": exc.error_code, "message": exc.message}},
            status_code=exc.status_code,
        )

    @app.exception_handler(Exception)
    async def _handle_unhandled(request: Request, exc: Exception) -> JSONResponse:
        log.error("unhandled_exception", error=str(exc), exc_info=True)
        return JSONResponse({"error": {"code": "internal_error"}}, status_code=500)

    # Routes
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(generate.router)
    app.include_router(chat.router)
    app.include_router(models.router)
    app.include_router(metrics.router)
    app.include_router(admin.router)

    instrument_fastapi(app)
    return app


app = create_app()
