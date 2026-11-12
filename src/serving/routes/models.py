"""List available models."""
from __future__ import annotations

import time

from fastapi import APIRouter, Depends

from src.serving.dependencies import get_engine
from src.serving.engine import LLMEngine
from src.serving.schemas import ModelInfo
from src.utils.auth import Principal, require_scopes

router = APIRouter()


@router.get("/v1/models")
async def list_models(
    principal: Principal = Depends(require_scopes("models:list")),
    engine: LLMEngine = Depends(get_engine),
) -> dict:
    return {
        "object": "list",
        "data": [
            ModelInfo(
                id=engine.model_name, created=int(time.time()), owned_by="llm-forge"
            ).model_dump()
        ],
    }
