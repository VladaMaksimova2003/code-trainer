from datetime import UTC, datetime, timedelta

import jwt

from shared.exceptions import AuthError

_STATE_TYP = "oauth_state"
_STATE_TTL_MINUTES = 10


def create_oauth_state_token(
    *,
    provider: str,
    code_verifier: str,
    secret_key: str,
    algorithm: str = "HS256",
) -> str:
    payload = {
        "typ": _STATE_TYP,
        "provider": provider,
        "cv": code_verifier,
        "exp": datetime.now(UTC) + timedelta(minutes=_STATE_TTL_MINUTES),
    }
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_oauth_state_token(
    state: str,
    *,
    secret_key: str,
    algorithm: str = "HS256",
) -> dict[str, str]:
    try:
        payload = jwt.decode(state, secret_key, algorithms=[algorithm])
    except jwt.PyJWTError as exc:
        raise AuthError("Invalid OAuth state.") from exc

    if payload.get("typ") != _STATE_TYP:
        raise AuthError("Invalid OAuth state.")
    provider = str(payload.get("provider") or "").strip()
    code_verifier = str(payload.get("cv") or "").strip()
    if not provider or not code_verifier:
        raise AuthError("Invalid OAuth state.")
    return {"provider": provider, "code_verifier": code_verifier}
