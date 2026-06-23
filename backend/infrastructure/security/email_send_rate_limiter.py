from __future__ import annotations

import hashlib
import os

import redis

from shared.config import Settings, get_settings


class EmailSendRateLimitError(Exception):
    def __init__(self, retry_after_seconds: int) -> None:
        self.retry_after_seconds = max(1, retry_after_seconds)
        super().__init__(
            f"Too many verification emails sent. Try again in {self.retry_after_seconds} seconds."
        )


def _hash_email(email: str) -> str:
    return hashlib.sha256(email.strip().lower().encode("utf-8")).hexdigest()[:24]


def _normalize_ip(ip_address: str | None) -> str:
    return (ip_address or "unknown").strip().lower().replace(":", "_")


class EmailSendRateLimiter:
    """Limits how often verification codes can be sent to an email or from an IP."""

    _EMAIL_PREFIX = "auth:email:send:email:"
    _IP_PREFIX = "auth:email:send:ip:"
    _MAX_PER_EMAIL = 5
    _MAX_PER_IP = 30
    _WINDOW_SECONDS = 10 * 60

    def __init__(
        self,
        client: redis.Redis | None = None,
        settings: Settings | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        redis_settings = self._settings.redis
        self._client = client or redis.Redis(
            host=os.getenv("REDIS_HOST", redis_settings.host),
            port=int(os.getenv("REDIS_PORT", str(redis_settings.port))),
            db=int(os.getenv("REDIS_DB", str(redis_settings.db))),
            decode_responses=True,
        )

    def check_and_register(self, *, email: str, purpose: str, ip_address: str | None) -> None:
        email_key = f"{self._EMAIL_PREFIX}{purpose}:{_hash_email(email)}"
        ip_key = f"{self._IP_PREFIX}{_normalize_ip(ip_address)}"

        email_retry = self._increment_if_over_limit(email_key, self._MAX_PER_EMAIL)
        if email_retry is not None:
            raise EmailSendRateLimitError(email_retry)

        ip_retry = self._increment_if_over_limit(ip_key, self._MAX_PER_IP)
        if ip_retry is not None:
            raise EmailSendRateLimitError(ip_retry)

    def _increment_if_over_limit(self, key: str, limit: int) -> int | None:
        count = int(self._client.incr(key))
        if count == 1:
            self._client.expire(key, self._WINDOW_SECONDS)
        if count > limit:
            ttl = int(self._client.ttl(key))
            return ttl if ttl > 0 else self._WINDOW_SECONDS
        return None
