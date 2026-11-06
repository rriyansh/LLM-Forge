"""vLLM AsyncLLMEngine wrapper."""

from __future__ import annotations

from typing import Any

try:
    from vllm import AsyncLLMEngine  # type: ignore
    from vllm.engine.arg_utils import AsyncEngineArgs  # type: ignore
except Exception:  # pragma: no cover
    AsyncLLMEngine = Any  # type: ignore
    AsyncEngineArgs = Any  # type: ignore


class vLLMEngine:
    """Wrapper around vLLM AsyncLLMEngine for text generation."""

    def __init__(self, model: str, **kwargs: Any) -> None:
        self.model = model
        self.kwargs = kwargs
        self.engine: Any = None

    async def start(self) -> None:
        if AsyncLLMEngine is None:
            raise RuntimeError("vLLM is required for serving")
        engine_args = AsyncEngineArgs(model=self.model, **self.kwargs)
        self.engine = AsyncLLMEngine.from_engine_args(engine_args)

    async def generate(self, prompt: str, sampling_params: dict[str, Any]) -> str:
        if self.engine is None:
            await self.start()
        from vllm import SamplingParams  # type: ignore

        params = SamplingParams(**sampling_params)
        request_id = "0"
        async for output in self.engine.generate(prompt, params, request_id):
            pass
        return output.outputs[0].text

    async def stop(self) -> None:
        self.engine = None
