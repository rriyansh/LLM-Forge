"""Shared fixtures. Sets safe test env vars BEFORE imports."""
from __future__ import annotations

import os

os.environ.setdefault("API_KEY", "a" * 40)
os.environ.setdefault("JWT_SECRET_KEY", "b" * 64)
os.environ.setdefault("REQUEST_SIGNING_KEY", "c" * 40)
os.environ.setdefault("ENV", "test")
os.environ.setdefault("MERGED_MODEL_PATH", "dummy-model")
os.environ.setdefault("SEMANTIC_CACHE_ENABLED", "false")
os.environ.setdefault("OTEL_ENABLED", "false")
os.environ.setdefault("MODEL_WARMUP_ENABLED", "false")

import pytest  # noqa: E402


@pytest.fixture
def api_key() -> str:
    return os.environ["API_KEY"]


@pytest.fixture
def jwt_secret() -> str:
    return os.environ["JWT_SECRET_KEY"]
