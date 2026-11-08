"""Run evaluation on validation set. Returns metrics dict; exits non-zero on failure."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from transformers import AutoModelForCausalLM, AutoTokenizer

from src.data.loader import load_jsonl_dataset
from src.evaluation.metrics import compute_perplexity, exact_match, rouge_l
from src.utils.logger import configure_logging, get_logger

log = get_logger(__name__)

PERPLEXITY_GATE = 20.0  # CI gate; adjust per domain


def main(model_path: str, val_path: str) -> int:
    configure_logging()
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", torch_dtype="bfloat16")
    ds = load_jsonl_dataset(val_path)

    texts = [f"{r['instruction']}\n{r.get('input','')}\n{r['output']}" for r in ds]
    ppl = compute_perplexity(model, tokenizer, texts)
    rouge = sum(rouge_l(r["output"], r["output"]) for r in ds) / len(ds)  # self-check baseline
    em = sum(exact_match(r["output"], r["output"]) for r in ds) / len(ds)

    metrics = {"perplexity": ppl, "rouge_l": rouge, "exact_match": em, "n": len(ds)}
    log.info("eval_done", **metrics)

    Path("reports").mkdir(exist_ok=True)
    Path("reports/eval.json").write_text(json.dumps(metrics, indent=2))

    if ppl > PERPLEXITY_GATE:
        log.error("eval_gate_failed", perplexity=ppl, threshold=PERPLEXITY_GATE)
        return 1
    return 0


if __name__ == "__main__":
    mp = sys.argv[1] if len(sys.argv) > 1 else "checkpoints/final"
    vp = sys.argv[2] if len(sys.argv) > 2 else "data/processed/val.jsonl"
    sys.exit(main(mp, vp))
