from __future__ import annotations

import os

QUEUE_NAME = os.getenv("SUBMISSION_QUEUE", "submissions:queue")
RESULT_PREFIX = os.getenv("SUBMISSION_RESULT_PREFIX", "submissions:result:")
LINT_QUEUE_NAME = os.getenv("LINT_QUEUE", "lint:queue")
LINT_RESULT_PREFIX = os.getenv("LINT_RESULT_PREFIX", "lint:result:")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
POLL_TIMEOUT_SECONDS = int(os.getenv("WORKER_POLL_TIMEOUT_SECONDS", "5"))
