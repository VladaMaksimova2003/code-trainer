"""Single rule: required ⊆ detected (with min_count) → PASS, else FAIL."""
from __future__ import annotations

from domain.analysis.core_detection import CoreDetectionResult
from domain.analysis.semantic_core import (
    ExamResult,
    RequiredStructureSpec,
    ValidationStatus,
)


def grade(
    required: list[RequiredStructureSpec],
    detected: CoreDetectionResult,
) -> ExamResult:
    missing = tuple(
        spec.type for spec in required if not detected.has(spec.type, spec.min_count)
    )
    present = tuple(
        spec.type for spec in required if detected.has(spec.type, spec.min_count)
    )
    status: ValidationStatus = "PASS" if not missing else "FAIL"
    return ExamResult(result=status, core=detected, missing=missing, present=present)
