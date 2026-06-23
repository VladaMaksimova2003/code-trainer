"""Redis-backed execution rate limits (submit-time only)."""
from __future__ import annotations

import redis

from worker.execution_settings import (
    EXECUTION_GLOBAL_DEPTH_KEY,
    EXECUTION_GLOBAL_MAX_QUEUE,
    EXECUTION_USER_LOCK_PREFIX,
    EXECUTION_USER_MAX_CONCURRENT,
    EXECUTION_USER_MAX_PER_MINUTE,
    RATE_LIMIT_WINDOW_SECONDS,
    REDIS_DB,
    REDIS_HOST,
    REDIS_PORT,
)


class ExecutionRateLimitError(Exception):
    def __init__(self, message: str, code: str = "RATE_LIMITED") -> None:
        super().__init__(message)
        self.code = code


class ExecutionRateLimiter:
    _USER_RATE_PREFIX = "execution:rate:"

    def __init__(self, client: redis.Redis | None = None) -> None:
        self._client = client or redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=True,
        )

    def check_submit(self, user_id: str, *, op: str | None = None) -> None:
        self._check_global_queue()
        if op != "lint_only":
            self._check_user_rate(user_id)
        self._check_user_concurrent(user_id)

    def on_job_queued(self, user_id: str) -> None:
        active_key = f"{EXECUTION_USER_LOCK_PREFIX}{user_id}:active"
        count = int(self._client.incr(active_key))
        if count == 1:
            self._client.expire(active_key, 120)

    def on_job_finished(self, user_id: str) -> None:
        active_key = f"{EXECUTION_USER_LOCK_PREFIX}{user_id}:active"
        depth = int(self._client.get(EXECUTION_GLOBAL_DEPTH_KEY) or 0)
        pipe = self._client.pipeline()
        if depth > 0:
            pipe.decr(EXECUTION_GLOBAL_DEPTH_KEY)
        current = int(self._client.get(active_key) or 0)
        if current > 0:
            pipe.decr(active_key)
        pipe.execute()

    def _check_global_queue(self) -> None:
        depth = int(self._client.get(EXECUTION_GLOBAL_DEPTH_KEY) or 0)
        if depth >= EXECUTION_GLOBAL_MAX_QUEUE:
            raise ExecutionRateLimitError(
                "Execution queue is full. Try again shortly.",
                code="QUEUE_FULL",
            )

    def _check_user_rate(self, user_id: str) -> None:
        rate_key = f"{self._USER_RATE_PREFIX}{user_id}"
        count = int(self._client.incr(rate_key))
        if count == 1:
            self._client.expire(rate_key, RATE_LIMIT_WINDOW_SECONDS)
        if count > EXECUTION_USER_MAX_PER_MINUTE:
            raise ExecutionRateLimitError(
                "Too many execution requests per minute.",
                code="USER_RATE_LIMIT",
            )

    def _check_user_concurrent(self, user_id: str) -> None:
        active = int(self._client.get(f"{EXECUTION_USER_LOCK_PREFIX}{user_id}:active") or 0)
        if active >= EXECUTION_USER_MAX_CONCURRENT:
            raise ExecutionRateLimitError(
                "Too many concurrent execution jobs.",
                code="USER_CONCURRENT_LIMIT",
            )
