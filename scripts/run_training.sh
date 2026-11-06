#!/usr/bin/env bash
set -euo pipefail

# Training command wrapper. Sets W&B environment variables and launches QLoRA training.

CONFIG="${1:-configs/training_config.yaml}"

export WANDB_PROJECT="${WANDB_PROJECT:-llm-forge}"
export WANDB_ENTITY="${WANDB_ENTITY:-}"
export WANDB_API_KEY="${WANDB_API_KEY:-}"
export HF_TOKEN="${HF_TOKEN:-}"

echo "Starting QLoRA training with config: $CONFIG"
python -m src.models.qlora_trainer --config "$CONFIG"
