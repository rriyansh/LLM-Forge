"""Security primitives: API keys, JWT, HMAC signing, PII, injection detection."""
from __future__ import annotations

import hashlib
import hmac
import re
import time
from datetime import UTC, datetime, timedelta
from functools import lru_cache
from typing import Any, Final

from jose import JWTError, jwt
from passlib.context import CryptContext
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

from src.utils.config_parser import get_env, load_security_config
from src.utils.exceptions import AuthError

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ---------- Passwords (for admin accounts) ----------
def hash_password(plain: str) -> str:
    return _pwd.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return _pwd.verify(plain, hashed)
    except Exception:
        return False


# ---------- API keys ----------
def constant_time_compare(a: str, b: str) -> bool:
    ah = hashlib.sha256(a.encode()).digest()
    bh = hashlib.sha256(b.encode()).digest()
    return hmac.compare_digest(ah, bh)


def verify_api_key(provided: str | None, expected: str) -> bool:
    if not provided or not expected:
        return False
    return constant_time_compare(provided, expected)


# ---------- JWT ----------
@lru_cache(maxsize=1)
def _jwt_settings() -> tuple[str, str, int, int, str, str]:
    cfg = load_security_config().auth
    secret = get_env("JWT_SECRET_KEY", required=True)
    if len(secret) < 32:
        raise RuntimeError("JWT_SECRET_KEY must be >=32 chars")
    return (
        secret,
        cfg.jwt_algorithm,
        cfg.access_ttl_seconds,
        cfg.refresh_ttl_seconds,
        cfg.issuer,
        cfg.audience,
    )


def create_access_token(sub: str, *, role: str, tenant: str, extra: dict[str, Any] | None = None) -> str:
    secret, algo, access_ttl, _, issuer, audience = _jwt_settings()
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": sub,
        "role": role,
        "tenant": tenant,
        "iat": int(now.timestamp()),
        "nbf": int(now.timestamp()),
        "exp": int((now + timedelta(seconds=access_ttl)).timestamp()),
        "iss": issuer,
        "aud": audience,
        "type": "access",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, secret, algorithm=algo)


def create_refresh_token(sub: str, *, tenant: str) -> str:
    secret, algo, _, refresh_ttl, issuer, audience = _jwt_settings()
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "sub": sub,
            "tenant": tenant,
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(seconds=refresh_ttl)).timestamp()),
            "iss": issuer,
            "aud": audience,
            "type": "refresh",
        },
        secret,
        algorithm=algo,
    )


def decode_token(token: str, *, expected_type: str = "access") -> dict[str, Any]:
    secret, algo, _, _, issuer, audience = _jwt_settings()
    try:
        payload = jwt.decode(
            token, secret, algorithms=[algo], issuer=issuer, audience=audience, options={"require_exp": True}
        )
    except JWTError as e:
        raise AuthError(f"invalid_token: {e}") from e
    if payload.get("type") != expected_type:
        raise AuthError("wrong_token_type")
    return payload


# ---------- HMAC request signing ----------
def sign_request(body: bytes, timestamp: int | None = None) -> tuple[str, int]:
    key = get_env("REQUEST_SIGNING_KEY", required=True).encode()
    ts = timestamp or int(time.time())
    msg = f"{ts}.".encode() + body
    sig = hmac.new(key, msg, hashlib.sha256).hexdigest()
    return sig, ts


def verify_request_signature(body: bytes, signature: str, timestamp: int, *, max_skew: int = 300) -> bool:
    if abs(int(time.time()) - timestamp) > max_skew:
        return False
    key = get_env("REQUEST_SIGNING_KEY", required=True).encode()
    msg = f"{timestamp}.".encode() + body
    expected = hmac.new(key, msg, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


# ---------- PII redaction (Presidio) ----------
_analyzer: AnalyzerEngine | None = None
_anonymizer: AnonymizerEngine | None = None


def _pii_engines() -> tuple[AnalyzerEngine, AnonymizerEngine]:
    global _analyzer, _anonymizer
    if _analyzer is None:
        _analyzer = AnalyzerEngine()
        _anonymizer = AnonymizerEngine()
    return _analyzer, _anonymizer


def redact_pii(text: str, entities: list[str] | None = None) -> str:
    if not text:
        return text
    analyzer, anonymizer = _pii_engines()
    try:
        results = analyzer.analyze(text=text, language="en", entities=entities)
    except Exception:
        return text  # fail open but log upstream
    if not results:
        return text
    return anonymizer.anonymize(text=text, analyzer_results=results).text


# ---------- Prompt injection heuristics ----------
_DEFAULT_INJECTION_PATTERNS: Final[list[str]] = [
    r"(?i)ignore\s+(all\s+)?(previous|above)\s+instructions",
    r"(?i)disregard\s+(the\s+)?(system|previous)\s+prompt",
    r"(?i)reveal\s+(your\s+)?(system\s+prompt|instructions|hidden\s+prompt)",
    r"(?i)you\s+are\s+now\s+(a|an|the)\s+",
    r"(?i)</?system>",
    r"(?i)\[\[?\s*system\s*\]\]?",
    r"(?i)repeat\s+the\s+above",
    r"(?i)print\s+(all\s+)?(your\s+)?(initial|system)\s+(prompt|message)",
]


@lru_cache(maxsize=1)
def _compiled_injection_patterns() -> list[re.Pattern[str]]:
    try:
        cfg = load_security_config().filters.injection
        pats = cfg.patterns or _DEFAULT_INJECTION_PATTERNS
    except Exception:
        pats = _DEFAULT_INJECTION_PATTERNS
    return [re.compile(p) for p in pats]


def detect_prompt_injection(text: str) -> bool:
    if not text:
        return False
    return any(p.search(text) for p in _compiled_injection_patterns())


# ---------- Input sanitization ----------
def sanitize_text(text: str, *, max_len: int = 32_000) -> str:
    if not text:
        return ""
    # strip NULs, control chars except newline/tab
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    return text[:max_len]


def ip_in_allowlist(ip: str, allowlist: str) -> bool:
    """allowlist is comma-separated CIDRs or exact IPs."""
    import ipaddress

    if not allowlist.strip():
        return True
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    for entry in allowlist.split(","):
        entry = entry.strip()
        if not entry:
            continue
        try:
            if "/" in entry:
                if addr in ipaddress.ip_network(entry, strict=False):
                    return True
            else:
                if addr == ipaddress.ip_address(entry):
                    return True
        except ValueError:
            continue
    return False
