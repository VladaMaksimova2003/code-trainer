"""Execution worker / Redis settings."""
from __future__ import annotations

import os

EXECUTION_QUEUE_PREFIX = os.getenv("EXECUTION_QUEUE_PREFIX", "execution:queue")
EXECUTION_QUEUE_DEFAULT = os.getenv("EXECUTION_QUEUE_DEFAULT", "execution:queue:default")
EXECUTION_JOB_KEY_PREFIX = os.getenv("EXECUTION_JOB_KEY_PREFIX", "execution:job:")
EXECUTION_RESULT_PREFIX = os.getenv("EXECUTION_RESULT_PREFIX", "execution:result:")
EXECUTION_DEDUP_PREFIX = os.getenv("EXECUTION_DEDUP_PREFIX", "execution:dedup:")
EXECUTION_USER_LOCK_PREFIX = os.getenv("EXECUTION_USER_LOCK_PREFIX", "execution:user:")
EXECUTION_GLOBAL_DEPTH_KEY = os.getenv("EXECUTION_GLOBAL_DEPTH_KEY", "execution:metrics:queue_depth")

EXECUTION_JOB_TTL_SECONDS = int(os.getenv("EXECUTION_JOB_TTL_SECONDS", "3600"))
EXECUTION_DOCKER_TIMEOUT_SECONDS = int(os.getenv("EXECUTION_DOCKER_TIMEOUT_SECONDS", "5"))

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
POLL_TIMEOUT_SECONDS = int(os.getenv("WORKER_POLL_TIMEOUT_SECONDS", "5"))

EXECUTION_GLOBAL_MAX_QUEUE = int(os.getenv("EXECUTION_GLOBAL_MAX_QUEUE", "500"))
EXECUTION_USER_MAX_PER_MINUTE = int(os.getenv("EXECUTION_USER_MAX_PER_MINUTE", "60"))
EXECUTION_USER_MAX_CONCURRENT = int(os.getenv("EXECUTION_USER_MAX_CONCURRENT", "2"))

RATE_LIMIT_WINDOW_SECONDS = 60
