"""Short-lived OAuth state in Redis (PKCE verifier + provider)."""
from __future__ import annotations

import json
import os
import secrets

import redis

from shared.config import get_settings
from shared.exceptions import AuthError

_PREFIX = "oauth:state:"
_TTL_SECONDS = 600


def _redis_client() -> redis.Redis:
    settings = get_settings().redis
    return redis.Redis(
        host=os.getenv("REDIS_HOST", settings.host),
        port=int(os.getenv("REDIS_PORT", str(settings.port))),
        db=int(os.getenv("REDIS_DB", str(settings.db))),
        decode_responses=True,
    )


def create_oauth_state(*, provider: str, code_verifier: str) -> str:
    state = secrets.token_urlsafe(32)
    payload = json.dumps({"provider": provider, "cv": code_verifier}, ensure_ascii=True)
    _redis_client().setex(f"{_PREFIX}{state}", _TTL_SECONDS, payload)
    return state


def consume_oauth_state(state: str) -> dict[str, str]:
    token = str(state or "").strip()
    if not token:
        raise AuthError("Invalid OAuth state.")

    key = f"{_PREFIX}{token}"
    client = _redis_client()
    raw = client.get(key)
    if not raw:
        raise AuthError("Invalid OAuth state.")

    client.delete(key)
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AuthError("Invalid OAuth state.") from exc

    provider = str(data.get("provider") or "").strip()
    code_verifier = str(data.get("cv") or "").strip()
    if not provider or not code_verifier:
        raise AuthError("Invalid OAuth state.")
    return {"provider": provider, "code_verifier": code_verifier}
