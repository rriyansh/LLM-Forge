.PHONY: help install install-dev lint format test train serve docker-train docker-serve clean

help:
	@echo "LLM-Forge - available commands:"
	@echo "  make install        Install production deps"
	@echo "  make install-dev    Install dev deps"
	@echo "  make lint           Run ruff + mypy"
	@echo "  make format         Run black + ruff --fix"
	@echo "  make test           Run pytest"
	@echo "  make train          Run QLoRA training"
	@echo "  make serve          Start FastAPI + vLLM"
	@echo "  make docker-serve   Build + run serving container"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

lint:
	ruff check src tests
	mypy src

format:
	black src tests
	ruff check --fix src tests

test:
	pytest tests -v --cov=src

train:
	bash scripts/run_training.sh

serve:
	bash scripts/run_serving.sh

docker-train:
	docker build -f docker/Dockerfile.train -t llm-forge:train .

docker-serve:
	docker build -f docker/Dockerfile.serve -t llm-forge:serve .
	docker run --gpus all --env-file .env -p 8000:8000 llm-forge:serve

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov
