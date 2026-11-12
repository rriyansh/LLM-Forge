"""Download gated HF model with auth + resume."""
from __future__ import annotations

import os
import sys

from huggingface_hub import snapshot_download


def main() -> None:
    model_id = sys.argv[1] if len(sys.argv) > 1 else os.getenv("MODEL_ID", "meta-llama/Meta-Llama-3-8B")
    token = os.getenv("HF_TOKEN")
    if not token:
        print("WARN: HF_TOKEN not set. Gated models will fail.", file=sys.stderr)
    path = snapshot_download(
        repo_id=model_id,
        token=token,
        resume_download=True,
        ignore_patterns=["*.msgpack", "*.h5", "*.ot", "*.gguf"],
        max_workers=8,
    )
    print(path)


if __name__ == "__main__":
    main()
