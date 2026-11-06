"""Evaluation script that runs on the validation set."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None

try:
    import torch  # type: ignore
    from transformers import AutoModelForCausalLM, AutoTokenizer  # type: ignore
except Exception:  # pragma: no cover
    torch = None  # type: ignore
    AutoModelForCausalLM = None  # type: ignore
    AutoTokenizer = None  # type: ignore

from src.evaluation.metrics import perplexity, rouge_scores, accuracy


def load_config(path: str | Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to load configs")
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def evaluate(config_path: str | Path) -> None:
    config = load_config(config_path)
    model_cfg = config.get("model", {})
    data_cfg = config.get("data", {})

    if AutoModelForCausalLM is None:
        raise RuntimeError("transformers is required for evaluation")

    model_path = Path(model_cfg.get("output_dir", "./checkpoints")) / "merged"
    if not model_path.exists():
        model_path = Path(model_cfg["base_model_id"])

    tokenizer = AutoTokenizer.from_pretrained(str(model_path), token=model_cfg.get("hf_token"))
    model = AutoModelForCausalLM.from_pretrained(
        str(model_path),
        token=model_cfg.get("hf_token"),
        device_map="auto",
        torch_dtype=torch.float16,
    )
    model.eval()

    val_path = Path(data_cfg["val_file"])
    records = []
    with open(val_path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    total_loss = 0.0
    rouge_results: list[dict[str, float]] = []
    exact_matches = 0

    for record in records:
        prompt = record.get("text", "")
        reference = record.get("output", "")

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model(**inputs, labels=inputs["input_ids"])
            loss = outputs.loss.item()
        total_loss += loss

        generated_ids = model.generate(
            inputs["input_ids"],
            max_new_tokens=128,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
        prediction = tokenizer.decode(generated_ids[0], skip_special_tokens=True)

        rouge_results.append(rouge_scores(prediction, reference))
        if prediction.strip() == reference.strip():
            exact_matches += 1

    n = len(records)
    avg_loss = total_loss / n if n else 0.0
    metrics = {
        "perplexity": perplexity(avg_loss),
        "avg_loss": avg_loss,
        "accuracy": exact_matches / n if n else 0.0,
        "rouge1": sum(r["rouge1"] for r in rouge_results) / n if n else 0.0,
        "rouge2": sum(r["rouge2"] for r in rouge_results) / n if n else 0.0,
        "rougeL": sum(r["rougeL"] for r in rouge_results) / n if n else 0.0,
    }

    print(json.dumps(metrics, indent=2))

    out_path = Path(model_cfg.get("output_dir", "./checkpoints")) / "eval_metrics.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"Evaluation metrics saved to {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate model on validation set")
    parser.add_argument("--config", required=True, help="Path to training config YAML")
    args = parser.parse_args()
    evaluate(args.config)


if __name__ == "__main__":
    main()
