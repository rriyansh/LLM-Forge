#!/usr/bin/env bash
set -Eeuo pipefail
trap 'echo "[FATAL] line $LINENO"; exit 1' ERR

: "${WANDB_API_KEY:?Set WANDB_API_KEY}"
export WANDB_PROJECT="${WANDB_PROJECT:-llm-forge}"
export PYTHONPATH="${PYTHONPATH:-$(pwd)}"

DATA_PATH="${1:-data/processed/train.jsonl}"
echo ">>> Training with data: $DATA_PATH"
python -m src.models.qlora_trainer "$DATA_PATH"
