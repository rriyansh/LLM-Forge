"""FastAPI dependencies: engine, cache, config accessors."""
from __future__ import annotations

from fastapi import Request

from src.serving.cache import SemanticCache
from src.serving.engine import LLMEngine
from src.utils.exceptions import EngineNotReadyError


def get_engine(request: Request) -> LLMEngine:
    eng: LLMEngine | None = getattr(request.app.state, "engine", None)
    if eng is None or not eng.ready:
        raise EngineNotReadyError("engine_not_ready")
    return eng


def get_cache(request: Request) -> SemanticCache:
    return request.app.state.cache
