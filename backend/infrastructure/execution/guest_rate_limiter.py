"""IP-based rate limits for anonymous guest checks."""
from __future__ import annotations

import hashlib

import redis

from shared.config import get_settings
from worker.execution_settings import REDIS_DB, REDIS_HOST, REDIS_PORT

_GUEST_RATE_PREFIX = "guest:rate:"
_GUEST_ACTIVE_PREFIX = "guest:active:"
_WINDOW_SECONDS = 60


class GuestRateLimitError(Exception):
    pass


class GuestRateLimiter:
    def __init__(self, client: redis.Redis | None = None) -> None:
        self._client = client or redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
        )
        self._settings = get_settings().guest_mode

    @staticmethod
    def guest_user_id(client_ip: str) -> str:
        digest = hashlib.sha256(client_ip.encode("utf-8")).hexdigest()[:16]
        return f"guest:{digest}"

    def check_submit(self, client_ip: str) -> None:
        rate_key = f"{_GUEST_RATE_PREFIX}{client_ip}"
        count = int(self._client.incr(rate_key))
        if count == 1:
            self._client.expire(rate_key, _WINDOW_SECONDS)
        if count > self._settings.max_checks_per_minute:
            raise GuestRateLimitError("Too many guest checks per minute.")

        active_key = f"{_GUEST_ACTIVE_PREFIX}{client_ip}"
        active = int(self._client.get(active_key) or 0)
        if active >= self._settings.max_concurrent_checks:
            raise GuestRateLimitError("Guest check already in progress.")

    def on_job_queued(self, client_ip: str) -> None:
        active_key = f"{_GUEST_ACTIVE_PREFIX}{client_ip}"
        count = int(self._client.incr(active_key))
        if count == 1:
            self._client.expire(active_key, _WINDOW_SECONDS * 10)

    def on_job_finished(self, client_ip: str) -> None:
        active_key = f"{_GUEST_ACTIVE_PREFIX}{client_ip}"
        current = int(self._client.get(active_key) or 0)
        if current > 0:
            self._client.decr(active_key)
