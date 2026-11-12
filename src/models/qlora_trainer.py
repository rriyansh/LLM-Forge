"""QLoRA fine-tuning entrypoint: resilient, W&B-tracked, config-driven."""
from __future__ import annotations

import os
import sys

import torch
from datasets import Dataset
from peft import LoraConfig, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import SFTConfig, SFTTrainer

from src.data.loader import load_sft_dataset
from src.data.preprocessor import format_alpaca
from src.utils.config_parser import load_training_config
from src.utils.logger import configure_logging, get_logger

log = get_logger(__name__)


def _dtype(name: str) -> torch.dtype:
    return {"bfloat16": torch.bfloat16, "float16": torch.float16, "float32": torch.float32}[name]


def build(cfg) -> tuple[AutoModelForCausalLM, AutoTokenizer]:
    tokenizer = AutoTokenizer.from_pretrained(cfg.model.id, trust_remote_code=cfg.model.trust_remote_code)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    bnb = BitsAndBytesConfig(
        load_in_4bit=cfg.quantization.load_in_4bit,
        bnb_4bit_quant_type=cfg.quantization.bnb_4bit_quant_type,
        bnb_4bit_compute_dtype=_dtype(cfg.quantization.bnb_4bit_compute_dtype),
        bnb_4bit_use_double_quant=cfg.quantization.bnb_4bit_use_double_quant,
    )
    model = AutoModelForCausalLM.from_pretrained(
        cfg.model.id,
        quantization_config=bnb,
        device_map="auto",
        torch_dtype=_dtype(cfg.model.torch_dtype),
        trust_remote_code=cfg.model.trust_remote_code,
    )
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=cfg.training.gradient_checkpointing)
    return model, tokenizer


def main(data_path: str) -> None:
    configure_logging()
    cfg = load_training_config()
    ds: Dataset = load_sft_dataset(data_path)
    ds = ds.map(format_alpaca, remove_columns=[c for c in ds.column_names if c != "text"])
    log.info("dataset_prepared", rows=len(ds))

    model, tokenizer = build(cfg)

    peft_cfg = LoraConfig(
        r=cfg.lora.r,
        lora_alpha=cfg.lora.alpha,
        lora_dropout=cfg.lora.dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=cfg.lora.target_modules,
    )

    report_to = "none"
    if os.getenv("WANDB_API_KEY"):
        os.environ["WANDB_PROJECT"] = cfg.wandb.project
        if cfg.wandb.tags:
            os.environ["WANDB_TAGS"] = ",".join(cfg.wandb.tags)
        report_to = "wandb"

    args = SFTConfig(
        output_dir=cfg.training.output_dir,
        num_train_epochs=cfg.training.num_train_epochs,
        per_device_train_batch_size=cfg.training.per_device_train_batch_size,
        gradient_accumulation_steps=cfg.training.gradient_accumulation_steps,
        learning_rate=cfg.training.learning_rate,
        lr_scheduler_type=cfg.training.lr_scheduler_type,
        warmup_ratio=cfg.training.warmup_ratio,
        weight_decay=cfg.training.weight_decay,
        max_grad_norm=cfg.training.max_grad_norm,
        bf16=cfg.training.bf16,
        logging_steps=cfg.training.logging_steps,
        save_strategy=cfg.training.save_strategy,
        save_total_limit=cfg.training.save_total_limit,
        max_seq_length=cfg.training.max_seq_length,
        packing=cfg.training.packing,
        gradient_checkpointing=cfg.training.gradient_checkpointing,
        optim=cfg.training.optim,
        group_by_length=cfg.training.group_by_length,
        report_to=report_to,
        run_name=cfg.wandb.run_name,
    )

    trainer = SFTTrainer(
        model=model,
        args=args,
        train_dataset=ds,
        peft_config=peft_cfg,
        processing_class=tokenizer,
    )
    log.info("training_start")
    trainer.train()
    final = f"{cfg.training.output_dir}/final"
    trainer.save_model(final)
    tokenizer.save_pretrained(final)
    log.info("training_complete", path=final)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "data/processed/train.jsonl"
    main(path)
