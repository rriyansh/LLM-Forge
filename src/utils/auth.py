"""Authentication dependency + RBAC enforcement."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Header, Request

from src.utils.config_parser import load_security_config
from src.utils.exceptions import AuthError, ForbiddenError
from src.utils.logger import audit
from src.utils.security import decode_token, verify_api_key


@dataclass(frozen=True, slots=True)
class Principal:
    user_id: str
    role: str
    tenant: str
    method: str  # "jwt" | "apikey"


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def get_principal(
    request: Request,
    authorization: Annotated[str | None, Header()] = None,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> Principal:
    ip = _client_ip(request)
    path = request.url.path

    # 1) Bearer JWT
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:]
        try:
            payload = decode_token(token, expected_type="access")
        except AuthError as e:
            audit.auth_failure(reason=str(e), ip=ip, path=path)
            raise
        principal = Principal(
            user_id=str(payload.get("sub", "")),
            role=str(payload.get("role", "readonly")),
            tenant=str(payload.get("tenant", "default")),
            method="jwt",
        )
        audit.auth_success(user_id=principal.user_id, method="jwt", ip=ip, path=path)
        return principal

    # 2) X-API-Key (service-to-service)
    if x_api_key:
        import os

        expected = os.getenv("API_KEY", "")
        if verify_api_key(x_api_key, expected):
            principal = Principal(user_id="service", role="service", tenant="default", method="apikey")
            audit.auth_success(user_id=principal.user_id, method="apikey", ip=ip, path=path)
            return principal
        audit.auth_failure(reason="bad_api_key", ip=ip, path=path)
        raise AuthError("invalid_api_key")

    audit.auth_failure(reason="missing_credentials", ip=ip, path=path)
    raise AuthError("missing_credentials")


def require_scopes(*scopes: str):
    """Dependency factory: enforce that principal has at least one scope."""
    def _dep(principal: Annotated[Principal, Depends(get_principal)]) -> Principal:
        cfg = load_security_config()
        allowed = set(cfg.rbac.scopes_for(principal.role))
        if "*" in allowed:
            return principal
        if not any(s in allowed for s in scopes):
            raise ForbiddenError(f"missing_scopes: {sorted(set(scopes) - allowed)}")
        return principal

    return _dep
