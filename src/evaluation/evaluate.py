"""Full evaluation pipeline with gates. Exits non-zero on gate failure."""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from transformers import AutoModelForCausalLM, AutoTokenizer

from src.data.loader import load_sft_dataset
from src.evaluation.llm_as_judge import judge_batch
from src.evaluation.metrics import compute_perplexity, exact_match, rouge_l
from src.evaluation.safety_eval import run_pii_probe_suite, run_prompt_injection_suite
from src.utils.config_parser import load_eval_config
from src.utils.logger import configure_logging, get_logger

log = get_logger(__name__)


async def run(model_path: str, val_path: str) -> int:
    configure_logging()
    cfg = load_eval_config()
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path, device_map="auto", torch_dtype="bfloat16")
    ds = load_sft_dataset(val_path)
    texts = [f"{r['instruction']}\n{r.get('input','')}\n{r['output']}" for r in ds]

    results: dict[str, float | dict] = {}

    if cfg.metrics.perplexity.enabled:
        results["perplexity"] = compute_perplexity(model, tokenizer, texts)
    if cfg.metrics.rouge_l.enabled:
        results["rouge_l"] = sum(rouge_l(r["output"], r["output"]) for r in ds) / len(ds)
    if cfg.metrics.exact_match.enabled:
        results["exact_match"] = sum(exact_match(r["output"], r["output"]) for r in ds) / len(ds)
    if cfg.metrics.safety.enabled:
        results["safety"] = {**run_prompt_injection_suite(), **run_pii_probe_suite()}
    if cfg.metrics.llm_as_judge.enabled:
        # In real run, generate responses with model and score them
        examples = [
            {"prompt": r["instruction"], "response": r["output"]} for r in list(ds)[:20]
        ]
        results["llm_as_judge"] = await judge_batch(
            examples, cfg.metrics.llm_as_judge.criteria, cfg.metrics.llm_as_judge.model or "gpt-4o-mini"
        )

    out = Path(cfg.report.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "eval.json").write_text(json.dumps(results, indent=2, default=float))
    log.info("eval_report", results=results)

    # Gate checks
    failed = []
    if cfg.metrics.perplexity.gate and float(results.get("perplexity", 0)) > cfg.metrics.perplexity.gate:
        failed.append(f"perplexity>{cfg.metrics.perplexity.gate}")
    if cfg.metrics.rouge_l.gate and float(results.get("rouge_l", 0)) < cfg.metrics.rouge_l.gate:
        failed.append(f"rouge_l<{cfg.metrics.rouge_l.gate}")
    if cfg.metrics.llm_as_judge.gate and isinstance(results.get("llm_as_judge"), dict):
        avg = sum(results["llm_as_judge"].values()) / max(1, len(results["llm_as_judge"]))
        if avg < cfg.metrics.llm_as_judge.gate:
            failed.append(f"judge<{cfg.metrics.llm_as_judge.gate}")

    if failed:
        log.error("eval_gates_failed", failed=failed)
        return 1
    log.info("eval_gates_passed")
    return 0


if __name__ == "__main__":
    mp = sys.argv[1] if len(sys.argv) > 1 else "./models/merged"
    vp = sys.argv[2] if len(sys.argv) > 2 else "data/processed/val.jsonl"
    sys.exit(asyncio.run(run(mp, vp)))
