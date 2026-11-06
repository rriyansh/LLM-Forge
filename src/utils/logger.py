"""Structured logging setup."""

from __future__ import annotations

import logging
import logging.config
from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


def setup_logging(config_path: str | Path | None = None) -> None:
    """Configure logging from a YAML config or fall back to basic config."""
    if config_path is not None and yaml is not None:
        with open(config_path, "r", encoding="utf-8") as fh:
            config = yaml.safe_load(fh)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        )


def get_logger(name: str) -> logging.Logger:
    """Return a logger for the given name."""
    return logging.getLogger(name)
