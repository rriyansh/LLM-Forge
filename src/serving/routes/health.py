"""Liveness + readiness + dependency probes."""
from __future__ import annotations

import os

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

from src import __version__
from src.serving.schemas import HealthResponse

router = APIRouter()


@router.get("/health/live", response_model=HealthResponse)
async def live() -> HealthResponse:
    return HealthResponse(status="alive", model_loaded=False, version=__version__)


@router.get("/health/ready")
async def ready(request: Request) -> JSONResponse:
    eng = getattr(request.app.state, "engine", None)
    ready = eng is not None and eng.ready
    deps: dict[str, str] = {"engine": "ok" if ready else "down"}

    # Optional: Redis
    if os.getenv("REDIS_URL"):
        try:
            from src.serving.quota import _client

            r = _client()
            deps["redis"] = "ok" if r is not None else "down"
        except Exception:  # noqa: BLE001
            deps["redis"] = "down"

    body = HealthResponse(
        status="ready" if ready else "not_ready",
        model_loaded=ready,
        version=__version__,
        dependencies=deps,
    ).model_dump()
    return JSONResponse(body, status_code=200 if ready else 503)
