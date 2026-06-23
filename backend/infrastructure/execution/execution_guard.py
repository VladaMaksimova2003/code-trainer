"""Prevent Docker execution outside worker processes."""
from __future__ import annotations

import os


class WorkerOnlyExecutionError(RuntimeError):
    pass


def assert_worker_context() -> None:
    if os.getenv("EXECUTION_WORKER") != "1":
        raise WorkerOnlyExecutionError(
            "Code execution is worker-only. Use ExecutionJobService.submit() from API."
        )


def mark_worker_context() -> None:
    os.environ["EXECUTION_WORKER"] = "1"
