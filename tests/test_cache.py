import pytest

from src.serving.cache import SemanticCache


@pytest.mark.asyncio
async def test_cache_disabled_by_default():
    c = SemanticCache()
    await c.set("p", {}, "v")
    assert await c.get("p", {}) is None
