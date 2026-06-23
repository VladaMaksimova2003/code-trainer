from __future__ import annotations

import hashlib
import os

import redis

from shared.config import Settings, get_settings


class AuthRateLimitError(Exception):
    def __init__(self, retry_after_seconds: int) -> None:
        self.retry_after_seconds = max(1, retry_after_seconds)
        super().__init__(
            f"Too many login attempts. Try again in {self.retry_after_seconds} seconds."
        )


def _normalize_ip(ip_address: str | None) -> str:
    return (ip_address or "unknown").strip().lower().replace(":", "_")


def _normalize_email(email: str) -> str:
    return email.strip().lower()


def _hash_email(email: str) -> str:
    return hashlib.sha256(_normalize_email(email).encode("utf-8")).hexdigest()[:24]


class AuthRateLimiter:
    _EMAIL_FAIL_PREFIX = "auth:login:fail:email:"
    _IP_FAIL_PREFIX = "auth:login:fail:ip:"
    _EMAIL_BLOCK_PREFIX = "auth:login:block:email:"
    _IP_BLOCK_PREFIX = "auth:login:block:ip:"

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

    def check_allowed(self, email: str, ip_address: str | None) -> None:
        retry_after = max(
            self._ttl(self._email_block_key(email)),
            self._ttl(self._ip_block_key(ip_address)),
        )
        if retry_after > 0:
            raise AuthRateLimitError(retry_after)

    def register_failure(self, email: str, ip_address: str | None) -> None:
        self._increment(
            self._email_fail_key(email),
            self._email_block_key(email),
        )
        self._increment(
            self._ip_fail_key(ip_address),
            self._ip_block_key(ip_address),
        )

    def reset(self, email: str, ip_address: str | None) -> None:
        self._client.delete(
            self._email_fail_key(email),
            self._email_block_key(email),
            self._ip_fail_key(ip_address),
            self._ip_block_key(ip_address),
        )

    def _increment(self, counter_key: str, block_key: str) -> None:
        count = int(self._client.incr(counter_key))
        if count == 1:
            self._client.expire(counter_key, self._settings.auth.login_window_seconds)
        if count >= self._settings.auth.login_max_attempts:
            self._client.set(
                block_key,
                "1",
                ex=self._settings.auth.login_block_seconds,
            )

    def _ttl(self, key: str) -> int:
        ttl = int(self._client.ttl(key))
        return ttl if ttl > 0 else 0

    def _email_fail_key(self, email: str) -> str:
        return f"{self._EMAIL_FAIL_PREFIX}{_hash_email(email)}"

    def _email_block_key(self, email: str) -> str:
        return f"{self._EMAIL_BLOCK_PREFIX}{_hash_email(email)}"

    def _ip_fail_key(self, ip_address: str | None) -> str:
        return f"{self._IP_FAIL_PREFIX}{_normalize_ip(ip_address)}"

    def _ip_block_key(self, ip_address: str | None) -> str:
        return f"{self._IP_BLOCK_PREFIX}{_normalize_ip(ip_address)}"
