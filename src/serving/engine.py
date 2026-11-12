"""vLLM AsyncLLM wrapper with concurrency limiter and warmup."""
from __future__ import annotations

import asyncio
import uuid

from vllm import SamplingParams
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.v1.engine.async_llm import AsyncLLM

from src.utils.config_parser import FullServingConfig, get_env
from src.utils.logger import get_logger

log = get_logger(__name__)


class LLMEngine:
    def __init__(self, cfg: FullServingConfig) -> None:
        self._cfg = cfg
        self._engine: AsyncLLM | None = None
        self._lock = asyncio.Lock()
        self._sem = asyncio.Semaphore(cfg.limits.max_concurrent_requests)
        self._model_name: str = ""

    async def start(self, model_path: str) -> None:
        async with self._lock:
            if self._engine is not None:
                return
            self._model_name = model_path or get_env("MODEL_ID", required=True)
            log.info("engine_starting", model=self._model_name)
            args = AsyncEngineArgs(
                model=self._model_name,
                max_model_len=self._cfg.engine.max_model_len,
                gpu_memory_utilization=self._cfg.engine.gpu_memory_utilization,
                tensor_parallel_size=self._cfg.engine.tensor_parallel_size,
                max_num_seqs=self._cfg.engine.max_num_seqs,
                dtype=self._cfg.engine.dtype,
                trust_remote_code=self._cfg.engine.trust_remote_code,
                enable_prefix_caching=self._cfg.engine.enable_prefix_caching,
                enable_chunked_prefill=self._cfg.engine.enable_chunked_prefill,
                disable_log_requests=self._cfg.engine.disable_log_requests,
            )
            self._engine = AsyncLLM.from_engine_args(args)
            log.info("engine_ready")

    async def stop(self) -> None:
        async with self._lock:
            self._engine = None
            log.info("engine_stopped")

    @property
    def ready(self) -> bool:
        return self._engine is not None

    @property
    def model_name(self) -> str:
        return self._model_name

    async def generate(
        self, prompt: str, *, temperature: float, top_p: float, max_tokens: int, stop: list[str]
    ) -> tuple[str, int, int, str, str]:
        if self._engine is None:
            raise RuntimeError("Engine not initialized")
        sampling = SamplingParams(
            temperature=temperature, top_p=top_p, max_tokens=max_tokens, stop=stop or None
        )
        request_id = f"req-{uuid.uuid4().hex}"
        async with self._sem:
            final = None
            async for out in self._engine.generate(prompt, sampling, request_id):
                final = out
        if final is None or not final.outputs:
            return "", 0, 0, "error", request_id
        o = final.outputs[0]
        return (
            o.text,
            len(final.prompt_token_ids or []),
            len(o.token_ids or []),
            o.finish_reason or "stop",
            request_id,
        )


# Type used for DI; actual instance lives on app.state
