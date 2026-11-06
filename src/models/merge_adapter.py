"""Merge LoRA adapters into the base model."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

try:
    import torch  # type: ignore
    from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore
    from peft import PeftModel  # type: ignore
except Exception:  # pragma: no cover
    torch = None  # type: ignore
    AutoModelForCausalLM = None  # type: ignore
    AutoTokenizer = None  # type: ignore
    PeftModel = None  # type: ignore


def load_config(path: str | Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to load configs")
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def merge_adapter(
    base_model_id: str,
    adapter_path: str | Path,
    output_path: str | Path,
    hf_token: str | None = None,
) -> None:
    if AutoModelForCausalLM is None:
        raise RuntimeError("transformers/peft are required to merge adapters")

    model = AutoModelForCausalLM.from_pretrained(
        base_model_id,
        token=hf_token,
        trust_remote_code=True,
        torch_dtype=torch.float16,
        device_map="auto",
    )
    model = PeftModel.from_pretrained(model, str(adapter_path))
    model = model.merge_and_unload()

    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(output_path))
    tokenizer = AutoTokenizer.from_pretrained(base_model_id, token=hf_token)
    tokenizer.save_pretrained(str(output_path))
    print(f"Merged model saved to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Merge LoRA adapter into base model")
    parser.add_argument("--config", required=True, help="Path to training config YAML")
    args = parser.parse_args()

    import yaml

    with open(args.config, "r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh)

    model_cfg = config.get("model", {})
    output_dir = Path(model_cfg.get("output_dir", "./checkpoints"))
    merge_adapter(
        base_model_id=model_cfg["base_model_id"],
        adapter_path=output_dir,
        output_path=output_dir / "merged",
        hf_token=model_cfg.get("hf_token"),
    )


if __name__ == "__main__":
    main()
