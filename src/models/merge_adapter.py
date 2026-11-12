"""Merge LoRA adapter into base weights for standalone serving."""
from __future__ import annotations

import argparse

from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.utils.logger import configure_logging, get_logger

log = get_logger(__name__)


def merge(base_id: str, adapter_path: str, out_path: str) -> None:
    tokenizer = AutoTokenizer.from_pretrained(adapter_path)
    base = AutoModelForCausalLM.from_pretrained(base_id, device_map="cpu", torch_dtype="bfloat16")
    model = PeftModel.from_pretrained(base, adapter_path)
    merged = model.merge_and_unload()
    merged.save_pretrained(out_path, safe_serialization=True)
    tokenizer.save_pretrained(out_path)
    log.info("merged", out=out_path)


if __name__ == "__main__":
    configure_logging()
    p = argparse.ArgumentParser()
    p.add_argument("--base", required=True)
    p.add_argument("--adapter", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    merge(a.base, a.adapter, a.out)
