# LLM-Forge

Production-ready LLM fine-tuning and serving framework built with QLoRA, PEFT, TRL, vLLM, and FastAPI.

## Project structure

```
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── Makefile
├── pyproject.toml
├── requirements.txt
├── .github/workflows/ci.yml
├── .github/workflows/cd.yml
├── configs/
├── data/
├── src/
├── notebooks/
├── scripts/
├── tests/
├── docker/
├── deployment/
├── monitoring/
├── checkpoints/
└── logs/
```

## Setup

```bash
# Clone the repository
git clone https://github.com/rriyansh/LLM-Forge.git
cd LLM-Forge

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
make install

# Copy environment template and fill in values
cp .env.example .env
```

## Usage

```bash
# Prepare data
python -m src.data.data_prep

# Fine-tune with QLoRA
make train

# Merge LoRA adapter into base model
python -m src.models.merge_adapter

# Evaluate the model
python -m src.evaluation.evaluate

# Start the serving API
make serve

# Run smoke test
bash scripts/test_api.sh
```

## Commands

| Command | Description |
|---------|-------------|
| `make install` | Install Python dependencies |
| `make lint` | Run ruff + black checks |
| `make test` | Run pytest |
| `make train` | Start QLoRA fine-tuning |
| `make serve` | Start vLLM + FastAPI server |
| `make format` | Format code with black |

## License

MIT License. See [LICENSE](LICENSE).
