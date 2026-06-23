"""TestCaseRunner — worker-only; API must use ExecutionJobService."""
from __future__ import annotations

from infrastructure.execution.execution_core import ExecutionCore
from infrastructure.execution.execution_guard import assert_worker_context
from infrastructure.execution.test_case_result import TestCaseResult

__all__ = ["TestCaseResult", "TestCaseRunner"]


class TestCaseRunner:
    def __init__(self, core: ExecutionCore | None = None) -> None:
        self._core = core or ExecutionCore()

    def run(
        self,
        code: str,
        language: str,
        test_cases: list[dict],
    ) -> list[TestCaseResult]:
        assert_worker_context()
        return self._core.run_tests(str(language).lower(), code, test_cases)
