"""Download gated model after `huggingface-cli login`."""
import os
import sys

from huggingface_hub import snapshot_download

model_id = sys.argv[1] if len(sys.argv) > 1 else os.getenv("MODEL_ID", "meta-llama/Meta-Llama-3-8B")
path = snapshot_download(
    repo_id=model_id,
    token=os.getenv("HF_TOKEN"),
    ignore_patterns=["*.msgpack", "*.h5", "*.ot"],
)
print(path)
