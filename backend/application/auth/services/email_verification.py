from __future__ import annotations

import hashlib
import logging
import os
import random
import re

import redis

from shared.config import get_settings
from shared.exceptions import EmailVerificationError

logger = logging.getLogger(__name__)

_PURPOSES = frozenset({"register", "change_email", "reset_password"})
_TTL_SECONDS = 10 * 60
_CODE_RE = re.compile(r"^\d{6}$")
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_CODE_KEY_PREFIX = "auth:email:code:"


def _hash_email(email: str) -> str:
    return hashlib.sha256(email.encode("utf-8")).hexdigest()[:24]


class EmailVerificationService:
    """Email verification codes stored in Redis with TTL."""

    def __init__(self, client: redis.Redis | None = None) -> None:
        if client is not None:
            self._client = client
            return
        settings = get_settings()
        redis_settings = settings.redis
        self._client = redis.Redis(
            host=os.getenv("REDIS_HOST", redis_settings.host),
            port=int(os.getenv("REDIS_PORT", str(redis_settings.port))),
            db=int(os.getenv("REDIS_DB", str(redis_settings.db))),
            decode_responses=True,
        )

    @staticmethod
    def normalize_email(email: str) -> str:
        return email.strip().lower()

    @classmethod
    def validate_email_address(cls, email: str) -> str:
        normalized = cls.normalize_email(email)
        if not _EMAIL_RE.match(normalized):
            raise EmailVerificationError("Укажите корректный email.")
        return normalized

    def _code_key(self, normalized: str, purpose: str) -> str:
        return f"{_CODE_KEY_PREFIX}{purpose}:{_hash_email(normalized)}"

    def issue_code(self, email: str, *, purpose: str) -> str:
        if purpose not in _PURPOSES:
            raise EmailVerificationError("Invalid verification purpose.")
        normalized = self.validate_email_address(email)

        code = f"{random.randint(0, 999999):06d}"
        key = self._code_key(normalized, purpose)
        self._client.setex(key, _TTL_SECONDS, code)
        logger.debug("Issued email verification code for %s purpose=%s", normalized, purpose)
        return code

    def _validate_stored_code(self, normalized: str, *, purpose: str, raw: str) -> None:
        if purpose not in _PURPOSES:
            raise EmailVerificationError("Invalid verification purpose.")
        if not _CODE_RE.match(raw):
            raise EmailVerificationError("Verification code must be 6 digits.")

        key = self._code_key(normalized, purpose)
        stored = self._client.get(key)
        if stored is None:
            raise EmailVerificationError("Verification code was not sent or has expired.")
        if stored != raw:
            raise EmailVerificationError("Invalid verification code.")

    def check_code(self, email: str, *, purpose: str, code: str) -> None:
        normalized = self.normalize_email(email)
        raw = (code or "").strip()
        self._validate_stored_code(normalized, purpose=purpose, raw=raw)

    def verify_and_consume(self, email: str, *, purpose: str, code: str) -> None:
        normalized = self.normalize_email(email)
        raw = (code or "").strip()
        self._validate_stored_code(normalized, purpose=purpose, raw=raw)
        key = self._code_key(normalized, purpose)
        self._client.delete(key)


email_verification_service = EmailVerificationService()
