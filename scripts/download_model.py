"""Download the base model from the Hugging Face Hub."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

try:
    from huggingface_hub import snapshot_download  # type: ignore
except Exception:  # pragma: no cover
    snapshot_download = None  # type: ignore


def download_model(model_id: str, output_dir: str | Path, token: str | None = None) -> None:
    if snapshot_download is None:
        raise RuntimeError("huggingface_hub is required to download models")
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        repo_id=model_id,
        local_dir=str(output_dir),
        token=token,
        local_dir_use_symlinks=False,
    )
    print(f"Model downloaded to {output_dir}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Download base model from Hugging Face")
    parser.add_argument("--model-id", required=True, help="Hugging Face model ID")
    parser.add_argument("--output-dir", default="./models/llama-3-8b")
    parser.add_argument("--token", default=None, help="HF token (or set HF_TOKEN env)")
    args = parser.parse_args()

    token = args.token or os.environ.get("HF_TOKEN")
    download_model(args.model_id, args.output_dir, token)


if __name__ == "__main__":
    main()
