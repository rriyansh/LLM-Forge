#!/usr/bin/env bash
set -euo pipefail
export WANDB_PROJECT="${WANDB_PROJECT:-llm-forge}"
: "${WANDB_API_KEY:?Set WANDB_API_KEY env var}"
python -m src.models.qlora_trainer "$@"
