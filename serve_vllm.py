import os
import uuid
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field
from vllm import SamplingParams
from vllm.engine.arg_utils import AsyncEngineArgs
from vllm.v1.engine.async_llm import AsyncLLM

# ---------------------------------------------------------
# Config: Fine-tuned model ka path ya HuggingFace ID
# ---------------------------------------------------------
MODEL_PATH = "./llm-forge-checkpoints/final"   # Ya "meta-llama/Meta-Llama-3-8B"
MAX_MODEL_LEN = 4096
GPU_MEMORY_UTILIZATION = 0.85

# Global engine (startup par initialize hoga)
engine: AsyncLLM = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: vLLM engine load karo. Shutdown: cleanup."""
    global engine
    print("vLLM engine loading...")
    engine = AsyncLLM.from_engine_args(
        AsyncEngineArgs(
            model=MODEL_PATH,
            max_model_len=MAX_MODEL_LEN,
            gpu_memory_utilization=GPU_MEMORY_UTILIZATION,
            trust_remote_code=True,
        )
    )
    print("vLLM engine ready.")
    yield
    # Shutdown (optional)
    engine = None


app = FastAPI(title="LLM-Forge Inference API", lifespan=lifespan)


# ---------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------
class GenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    temperature: float = 0.7
    max_tokens: int = 256


class GenerateResponse(BaseModel):
    text: str


# ---------------------------------------------------------
# Generation Endpoint
# ---------------------------------------------------------
@app.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    sampling_params = SamplingParams(
        temperature=request.temperature,
        max_tokens=request.max_tokens,
    )
    request_id = f"req-{uuid.uuid4().hex}"

    final_output = None
    async for output in engine.generate(
        request.prompt, sampling_params, request_id
    ):
        final_output = output

    if final_output is None or not final_output.outputs:
        return GenerateResponse(text="[ERROR] No output generated.")

    return GenerateResponse(text=final_output.outputs[0].text.strip())


# ---------------------------------------------------------
# Health Check
# ---------------------------------------------------------
@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
