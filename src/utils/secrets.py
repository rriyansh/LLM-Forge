"""Secret resolution: env vars first, optional HashiCorp Vault fallback."""
from __future__ import annotations

import os
from functools import lru_cache

from src.utils.config_parser import get_env_bool
from src.utils.logger import get_logger

log = get_logger(__name__)


@lru_cache(maxsize=128)
def _vault_client():  # pragma: no cover
    if not get_env_bool("VAULT_ENABLED", False):
        return None
    try:
        import hvac  # type: ignore

        client = hvac.Client(url=os.getenv("VAULT_ADDR"), token=os.getenv("VAULT_TOKEN"))
        if not client.is_authenticated():
            log.warning("vault_auth_failed")
            return None
        return client
    except Exception as e:  # noqa: BLE001
        log.warning("vault_init_failed", error=str(e))
        return None


def get_secret(key: str, *, required: bool = True) -> str:
    # 1) env
    val = os.getenv(key)
    if val:
        return val
    # 2) vault
    client = _vault_client()
    if client is not None:  # pragma: no cover
        try:
            path = os.getenv("VAULT_SECRET_PATH", "secret/data/llm-forge")
            resp = client.secrets.kv.v2.read_secret_version(path=path)
            val = resp.get("data", {}).get("data", {}).get(key)
            if val:
                os.environ[key] = val  # cache in env for subsequent lookups
                return val
        except Exception as e:  # noqa: BLE001
            log.warning("vault_fetch_failed", key=key, error=str(e))

    if required:
        raise RuntimeError(f"Secret not found: {key}")
    return ""
