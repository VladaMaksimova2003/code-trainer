"""Per-request execution user key for rate limiting."""
from __future__ import annotations

import contextvars

_user_key: contextvars.ContextVar[str] = contextvars.ContextVar(
    "execution_user_key",
    default="anonymous",
)


def set_execution_user_key(user_key: str) -> contextvars.Token[str]:
    return _user_key.set(user_key or "anonymous")


def reset_execution_user_key(token: contextvars.Token[str]) -> None:
    _user_key.reset(token)


def get_execution_user_key() -> str:
    return _user_key.get()


def get_execution_user_key() -> str:
    return _user_key.get()
