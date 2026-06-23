"""Optional stage timings for code execution (enable with EXECUTION_PROFILE=1)."""
from __future__ import annotations

import json
import logging
import os
import time
from contextlib import contextmanager
from typing import Any, Iterator

logger = logging.getLogger("execution.profile")


def profiling_enabled() -> bool:
    return os.getenv("EXECUTION_PROFILE", "").lower() in {"1", "true", "yes"}


class ExecutionProfiler:
    def __init__(self, *, language: str = "", op: str = "") -> None:
        self.language = language
        self.op = op
        self._stages: list[dict[str, Any]] = []
        self._t0 = time.perf_counter()

    @contextmanager
    def stage(self, name: str, **meta: Any) -> Iterator[None]:
        if not profiling_enabled():
            yield
            return
        started = time.perf_counter()
        try:
            yield
        finally:
            elapsed_ms = int((time.perf_counter() - started) * 1000)
            entry = {"stage": name, "ms": elapsed_ms, **meta}
            self._stages.append(entry)
            logger.info("execution_stage %s", json.dumps(entry, ensure_ascii=False))

    def mark(self, name: str, **meta: Any) -> None:
        if not profiling_enabled():
            return
        elapsed_ms = int((time.perf_counter() - self._t0) * 1000)
        entry = {"stage": name, "ms": elapsed_ms, **meta}
        self._stages.append(entry)
        logger.info("execution_stage %s", json.dumps(entry, ensure_ascii=False))

    def finish(self, **meta: Any) -> list[dict[str, Any]]:
        if not profiling_enabled():
            return []
        total_ms = int((time.perf_counter() - self._t0) * 1000)
        summary = {
            "stage": "total",
            "ms": total_ms,
            "language": self.language,
            "op": self.op,
            **meta,
            "stages": self._stages,
        }
        logger.info("execution_profile %s", json.dumps(summary, ensure_ascii=False))
        return self._stages
