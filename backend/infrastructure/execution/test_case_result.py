"""Shared test case result type for execution strategies."""
from __future__ import annotations

from typing import Any


class TestCaseResult:
    def __init__(
        self,
        case: int,
        status: str,
        inputs: str,
        expected: str,
        actual: str,
        message: str = "",
        duration_ms: int = 0,
    ):
        self.case = case
        self.status = status
        self.inputs = inputs
        self.expected = expected
        self.actual = actual
        self.message = message
        self.duration_ms = duration_ms

    def to_dict(self) -> dict[str, Any]:
        return {
            "case": self.case,
            "status": self.status,
            "inputs": self.inputs,
            "expected": self.expected,
            "actual": self.actual,
            "message": self.message,
            "duration_ms": self.duration_ms,
        }
