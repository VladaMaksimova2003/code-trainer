"""Core exam API — grading only, no analytics."""
from __future__ import annotations

from application.analysis.core.educational_validator import EducationalValidator
from domain.analysis.semantic_core import ExamResult, RequiredStructureSpec


class CoreExamService:
    def __init__(self, validator: EducationalValidator | None = None) -> None:
        self._validator = validator or EducationalValidator()

    def examine(
        self,
        code: str,
        language_id: str,
        required: list[RequiredStructureSpec] | list[str] | list[dict],
    ) -> ExamResult:
        return self._validator.validate(code, language_id, required)
