import pytest


@pytest.mark.gpu
@pytest.mark.skipif(not __import__("os").environ.get("RUN_GPU_TESTS"), reason="GPU test")
def test_engine_smoke():
    """Requires vLLM + GPU. Skipped unless RUN_GPU_TESTS=1."""
    from src.serving.engine import LLMEngine
    from src.utils.config_parser import load_serving_config

    eng = LLMEngine(load_serving_config())
    # would need real model; skip heavy path
