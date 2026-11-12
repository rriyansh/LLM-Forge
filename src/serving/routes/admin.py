"""Admin endpoints: reload engine, rotate API key, view usage.

These paths are gated by AdminAPIKeyMiddleware (static API_KEY only).
"""
from __future__ import annotations

import os

from fastapi import APIRouter, Depends

from src.serving.dependencies import get_engine
from src.serving.engine import LLMEngine
from src.utils.logger import audit, get_logger
from src.utils.metrics import CIRCUIT_STATE

log = get_logger(__name__)
router = APIRouter(prefix="/admin")


@router.get("/status")
async def status(engine: LLMEngine = Depends(get_engine)) -> dict:
    return {
        "model": engine.model_name,
        "ready": engine.ready,
        "env": os.getenv("ENV", "dev"),
    }


@router.post("/reload")
async def reload_engine(engine: LLMEngine = Depends(get_engine)) -> dict:
    audit.admin_action(user_id="admin", action="reload_engine", target=engine.model_name)
    await engine.stop()
    await engine.start(engine.model_name)
    return {"status": "reloaded"}


@router.get("/circuit/{name}")
async def circuit(name: str) -> dict:
    # Report current gauge value if exists
    try:
        val = CIRCUIT_STATE.labels(name=name)._value.get()  # noqa: SLF001
    except Exception:  # noqa: BLE001
        val = 0
    return {"name": name, "state": {0: "closed", 1: "half_open", 2: "open"}.get(int(val), "unknown")}
