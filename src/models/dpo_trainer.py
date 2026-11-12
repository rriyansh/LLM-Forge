"""DPO fine-tuning on preference data (chosen/rejected)."""
from __future__ import annotations

import os
import sys

import torch
from peft import LoraConfig
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from trl import DPOConfig, DPOTrainer

from src.data.loader import load_preference_dataset
from src.utils.config_parser import load_training_config
from src.utils.logger import configure_logging, get_logger

log = get_logger(__name__)


def _dtype(name: str) -> torch.dtype:
    return {"bfloat16": torch.bfloat16, "float16": torch.float16, "float32": torch.float32}[name]


def main(data_path: str) -> None:
    configure_logging()
    cfg = load_training_config()

    tokenizer = AutoTokenizer.from_pretrained(cfg.model.id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=_dtype(cfg.model.torch_dtype),
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        cfg.model.id,
        quantization_config=bnb,
        device_map="auto",
        torch_dtype=_dtype(cfg.model.torch_dtype),
    )

    ds = load_preference_dataset(data_path)
    log.info("preference_dataset_loaded", rows=len(ds))

    peft_cfg = LoraConfig(
        r=cfg.lora.r,
        lora_alpha=cfg.lora.alpha,
        lora_dropout=cfg.lora.dropout,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=cfg.lora.target_modules,
    )

    report_to = "wandb" if os.getenv("WANDB_API_KEY") else "none"
    args = DPOConfig(
        output_dir=f"{cfg.training.output_dir}/dpo",
        beta=cfg.dpo.beta,
        loss_type=cfg.dpo.loss_type,
        max_prompt_length=cfg.dpo.max_prompt_length,
        max_length=cfg.dpo.max_length,
        per_device_train_batch_size=cfg.training.per_device_train_batch_size,
        gradient_accumulation_steps=cfg.training.gradient_accumulation_steps,
        learning_rate=5e-5,
        num_train_epochs=1,
        bf16=True,
        logging_steps=10,
        save_strategy="epoch",
        report_to=report_to,
        run_name=f"{cfg.wandb.run_name}-dpo",
    )

    trainer = DPOTrainer(
        model=model,
        ref_model=None,  # uses implicit reference (PEFT)
        args=args,
        train_dataset=ds,
        peft_config=peft_cfg,
        processing_class=tokenizer,
    )
    trainer.train()
    trainer.save_model(f"{cfg.training.output_dir}/dpo/final")
    tokenizer.save_pretrained(f"{cfg.training.output_dir}/dpo/final")
    log.info("dpo_complete")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/processed/preferences.jsonl")
