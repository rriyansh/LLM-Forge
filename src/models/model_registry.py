"""Simple file-based model registry (versioned metadata)."""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

from src.utils.logger import get_logger

log = get_logger(__name__)


class ModelRegistry:
    def __init__(self, root: str = "./models") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.index_path = self.root / "registry.json"

    def _load(self) -> dict:
        if self.index_path.exists():
            return json.loads(self.index_path.read_text())
        return {"models": {}}

    def _save(self, data: dict) -> None:
        self.index_path.write_text(json.dumps(data, indent=2))

    def register(
        self,
        name: str,
        version: str,
        model_path: str,
        *,
        metrics: dict | None = None,
        base_model: str | None = None,
        metadata: dict | None = None,
    ) -> dict:
        data = self._load()
        key = f"{name}:{version}"
        entry = {
            "name": name,
            "version": version,
            "model_path": model_path,
            "base_model": base_model,
            "metrics": metrics or {},
            "metadata": metadata or {},
            "registered_at": time.time(),
        }
        data["models"][key] = entry
        self._save(data)
        log.info("model_registered", **entry)
        return entry

    def get(self, name: str, version: str = "latest") -> dict | None:
        data = self._load()
        if version == "latest":
            candidates = [
                (k, v) for k, v in data["models"].items() if v["name"] == name
            ]
            if not candidates:
                return None
            return max(candidates, key=lambda kv: kv[1]["registered_at"])[1]
        return data["models"].get(f"{name}:{version}")

    def list_versions(self, name: str) -> list[dict]:
        data = self._load()
        return [v for v in data["models"].values() if v["name"] == name]

    @staticmethod
    def file_hash(path: str) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
