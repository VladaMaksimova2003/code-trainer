"""Educational core — six structures, PASS/FAIL only."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from domain.analysis.core_detection import CoreDetectionResult

EducationalSemanticIR = CoreDetectionResult

CORE_STRUCTURE_IDS: frozenset[str] = frozenset(
    {
        "loop",
        "function",
        "call",
        "condition",
        "return",
        "assignment",
    }
)


def get_core_structure_ids() -> frozenset[str]:
    return CORE_STRUCTURE_IDS


ValidationStatus = Literal["PASS", "FAIL"]


@dataclass(frozen=True)
class RequiredStructureSpec:
    type: str
    min_count: int = 1


@dataclass(frozen=True)
class ExamResult:
    result: ValidationStatus
    core: CoreDetectionResult
    missing: tuple[str, ...] = ()
    present: tuple[str, ...] = ()

    @property
    def status(self) -> ValidationStatus:
        return self.result

    @property
    def is_valid(self) -> bool:
        return self.result == "PASS"

    def to_dict(self) -> dict:
        return {
            "result": self.result,
            "core": {
                "detected": sorted(self.core.detected),
                "missing": list(self.missing),
            },
        }


EducationalValidationResult = ExamResult
