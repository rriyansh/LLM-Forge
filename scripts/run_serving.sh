#!/usr/bin/env bash
set -euo pipefail

# Start vLLM + FastAPI serving server.

CONFIG="${1:-configs/serving_config.yaml}"
API_KEY="${API_KEY:-changeme}"

export API_KEY="$API_KEY"

echo "Starting vLLM + FastAPI server with config: $CONFIG"
python -m uvicorn src.serving.app:app --host 0.0.0.0 --port "${API_PORT:-8000}"
