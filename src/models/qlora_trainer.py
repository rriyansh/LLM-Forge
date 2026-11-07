"""QLoRA fine-tuning entrypoint. Secure, configurable, W&B tracked."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer

from src.data.loader import load_jsonl_dataset
from src.data.preprocessor import format_example
from src.utils.config_parser import load_training_config
from src.utils.logger import configure_logging, get_logger

log = get_logger(__name__)


def _dtype_from_str(name: str) -> torch.dtype:
    return {"bfloat16": torch.bfloat16, "float16": torch.float16, "float32": torch.float32}[name]


def build_model(cfg) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    log.info("loading_model", model_id=cfg.model.id)
    bnb = BitsAndBytesConfig(
        load_in_4bit=cfg.quantization.load_in_4bit,
        bnb_4bit_quant_type=cfg.quantization.bnb_4bit_quant_type,
        bnb_4bit_compute_dtype=_dtype_from_str(cfg.quantization.bnb_4bit_compute_dtype),
        bnb_4bit_use_double_quant=cfg.quantization.bnb_4bit_use_double_quant,
    )
    tokenizer = AutoTokenizer.from_pretrained(cfg.model.id, trust_remote_code=cfg.model.trust_remote_code)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        cfg.model.id,
        quantization_config=bnb,
        device_map="auto",
        torch_dtype=_dtype_from_str(cfg.model.torch_dtype),
        trust_remote_code=cfg.model.trust_remote_code,
    )
    model = prepare_model_for_kbit_training(
        model, use_gradient_checkpointing=cfg.training.gradient_checkpointing
    )
    return model, tokenizer


def main(data_path: str = "data/processed/train.jsonl") -> None:
    configure_logging()
    cfg = load_training_config()

    if not os.getenv("WANDB_API_KEY"):
        log.warning("wandb_api_key_missing", note="Set WANDB_API_KEY for tracking")
        report_to: str | list[str] = "none"
    else:
        report_to = "wandb"
        os.environ["WANDB_PROJECT"] = cfg.wandb.project

    ds: Dataset = load_jsonl_dataset(data_path)
    ds = ds.map(format_example, remove_columns=[c for c in ds.column_names if c != "text"])

    model, tokenizer = build_model(cfg)

    peft_cfg = LoraConfig(
        r=cfg.lora.r,
        lora_alpha=cfg.lora.alpha,
        lora_dropout=cfg.lora.dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=cfg.lora.target_modules,
    )

    out_dir = Path(cfg.training.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    sft_cfg = SFTConfig(
        output_dir=str(out_dir),
        num_train_epochs=cfg.training.num_train_epochs,
        per_device_train_batch_size=cfg.training.per_device_train_batch_size,
        gradient_accumulation_steps=cfg.training.gradient_accumulation_steps,
        learning_rate=cfg.training.learning_rate,
        lr_scheduler_type=cfg.training.lr_scheduler_type,
        warmup_ratio=cfg.training.warmup_ratio,
        bf16=cfg.training.bf16,
        logging_steps=cfg.training.logging_steps,
        save_strategy=cfg.training.save_strategy,
        save_total_limit=cfg.training.save_total_limit,
        max_seq_length=cfg.training.max_seq_length,
        packing=cfg.training.packing,
        gradient_checkpointing=cfg.training.gradient_checkpointing,
        optim=cfg.training.optim,
        report_to=report_to,
        run_name=cfg.wandb.run_name,
    )

    trainer = SFTTrainer(
        model=model,
        args=sft_cfg,
        train_dataset=ds,
        peft_config=peft_cfg,
        processing_class=tokenizer,
    )

    log.info("training_start", rows=len(ds))
    trainer.train()
    final_path = out_dir / "final"
    trainer.save_model(str(final_path))
    tokenizer.save_pretrained(str(final_path))
    log.info("training_complete", path=str(final_path))


if __name__ == "__main__":
    data_arg = sys.argv[1] if len(sys.argv) > 1 else "data/processed/train.jsonl"
    main(data_arg)
