.PHONY: install lint test format train serve train-docker serve-docker down

PYTHON ?= python
PIP ?= pip

install:
	$(PIP) install -r requirements.txt

lint:
	ruff check src tests scripts
	black --check src tests scripts

format:
	black src tests scripts
	ruff check --fix src tests scripts

test:
	$(PYTHON) -m pytest tests -v

train:
	WANDB_PROJECT=llm-forge $(PYTHON) -m src.models.qlora_trainer --config configs/training_config.yaml

merge:
	$(PYTHON) -m src.models.merge_adapter --config configs/training_config.yaml

evaluate:
	$(PYTHON) -m src.evaluation.evaluate --config configs/training_config.yaml

serve:
	bash scripts/run_serving.sh

prepare-data:
	$(PYTHON) -m src.data.data_prep

train-docker:
	docker compose -f docker/docker-compose.yml --profile train up --build llm-train

serve-docker:
	docker compose -f docker/docker-compose.yml --profile serve up --build llm-serve

down:
	docker compose -f docker/docker-compose.yml down
