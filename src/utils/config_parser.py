"""YAML config file loading utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml  # type: ignore
except Exception:  # pragma: no cover
    yaml = None


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a YAML config file into a dictionary."""
    if yaml is None:
        raise RuntimeError("PyYAML is required to load configs")
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def get(config: dict[str, Any], key: str, default: Any = None) -> Any:
    """Get a nested config value using dot notation."""
    parts = key.split(".")
    current: Any = config
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current
