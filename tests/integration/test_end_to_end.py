"""End-to-end against a real running server. Requires BASE_URL env."""
import os

import httpx
import pytest

BASE = os.getenv("BASE_URL")
pytestmark = pytest.mark.skipif(not BASE, reason="BASE_URL not set")


@pytest.mark.integration
def test_health():
    assert httpx.get(f"{BASE}/health/live", timeout=5).status_code == 200


@pytest.mark.integration
def test_auth_required():
    assert httpx.post(f"{BASE}/generate", json={"prompt": "hi"}, timeout=5).status_code == 401
