"""QLoRA fine-tuning main logic (PEFT + TRL)."""

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
    from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig  # type: ignore
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training  # type: ignore
    from trl import SFTTrainer, SFTConfig  # type: ignore
    from datasets import load_dataset  # type: ignore
except Exception:  # pragma: no cover - heavy deps may not be installed
    torch = None  # type: ignore
    AutoModelForCausalLM = None  # type: ignore
    AutoTokenizer = None  # type: ignore
    BitsAndBytesConfig = None  # type: ignore
    LoraConfig = None  # type: ignore
    get_peft_model = None  # type: ignore
    prepare_model_for_kbit_training = None  # type: ignore
    SFTTrainer = None  # type: ignore
    SFTConfig = None  # type: ignore
    load_dataset = None  # type: ignore


def load_config(path: str | Path) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to load configs")
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def train(config_path: str | Path) -> None:
    if torch is None:
        raise RuntimeError("torch/transformers/peft/trl are required for training")

    config = load_config(config_path)
    model_cfg = config.get("model", {})
    qlora_cfg = config.get("qlora", {})
    bnb_cfg = config.get("bnb", {})
    train_cfg = config.get("training", {})
    data_cfg = config.get("data", {})

    tokenizer = AutoTokenizer.from_pretrained(
        model_cfg["base_model_id"],
        token=model_cfg.get("hf_token"),
        trust_remote_code=model_cfg.get("trust_remote_code", False),
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    quantization_config = BitsAndBytesConfig(
        load_in_4bit=bnb_cfg.get("load_in_4bit", True),
        bnb_4bit_compute_dtype=getattr(torch, bnb_cfg.get("bnb_4bit_compute_dtype", "bfloat16")),
        bnb_4bit_quant_type=bnb_cfg.get("bnb_4bit_quant_type", "nf4"),
        bnb_4bit_use_double_quant=bnb_cfg.get("bnb_4bit_use_double_quant", True),
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_cfg["base_model_id"],
        quantization_config=quantization_config,
        device_map="auto",
        token=model_cfg.get("hf_token"),
        trust_remote_code=model_cfg.get("trust_remote_code", False),
        use_flash_attention_2=model_cfg.get("use_flash_attention_2", False),
    )
    model = prepare_model_for_kbit_training(model)

    peft_config = LoraConfig(
        r=qlora_cfg.get("r", 16),
        lora_alpha=qlora_cfg.get("lora_alpha", 32),
        lora_dropout=qlora_cfg.get("lora_dropout", 0.05),
        bias=qlora_cfg.get("bias", "none"),
        task_type=qlora_cfg.get("task_type", "CAUSAL_LM"),
        target_modules=qlora_cfg.get("target_modules", None),
    )
    model = get_peft_model(model, peft_config)

    train_dataset = load_dataset("json", data_files=data_cfg["train_file"], split="train")
    val_dataset = load_dataset("json", data_files=data_cfg["val_file"], split="train")

    sft_config = SFTConfig(
        output_dir=model_cfg.get("output_dir", "./checkpoints"),
        per_device_train_batch_size=train_cfg.get("per_device_train_batch_size", 4),
        per_device_eval_batch_size=train_cfg.get("per_device_eval_batch_size", 4),
        gradient_accumulation_steps=train_cfg.get("gradient_accumulation_steps", 4),
        learning_rate=train_cfg.get("learning_rate", 2e-4),
        num_train_epochs=train_cfg.get("num_train_epochs", 3),
        lr_scheduler_type=train_cfg.get("lr_scheduler_type", "cosine"),
        warmup_ratio=train_cfg.get("warmup_ratio", 0.03),
        weight_decay=train_cfg.get("weight_decay", 0.01),
        bf16=train_cfg.get("bf16", True),
        logging_steps=train_cfg.get("logging_steps, 10", 10),
        save_steps=train_cfg.get("save_steps", 500),
        eval_steps=train_cfg.get("eval_steps", 500),
        save_total_limit=train_cfg.get("save_total_limit", 3),
        seed=train_cfg.get("seed", 42),
        report_to=train_cfg.get("report_to", "wandb"),
        max_seq_length=data_cfg.get("max_seq_length", 2048),
    )

    trainer = SFTTrainer(
        model=model,
        args=sft_config,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        dataset_text_field="text",
    )
    trainer.train()
    trainer.save_model(model_cfg.get("output_dir", "./checkpoints"))
    tokenizer.save_pretrained(model_cfg.get("output_dir", "./checkpoints"))


def main() -> None:
    parser = argparse.ArgumentParser(description="QLoRA fine-tuning")
    parser.add_argument("--config", required=True, help="Path to training config YAML")
    args = parser.parse_args()
    train(args.config)


if __name__ == "__main__":
    main()
