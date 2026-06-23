"""Orchestrates profile update + error analysis + adaptive decision after core grading."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from application.analysis.core.exam_service import CoreExamService
from application.learning.adaptive.adaptive_learning_engine import (
    apply_decision_to_profile,
    decide_next_step,
    get_allowed_structures_for_profile,
)
from application.learning.adaptive.error_analysis import analyze_errors
from application.learning.adaptive.structure_profile_updater import apply_exam_to_profile
from domain.analysis.semantic_core import ExamResult, RequiredStructureSpec
from domain.learning.student_structure_profile import StudentStructureProfile
from infrastructure.repositories.learning.student_learning_profile_repository import (
    StudentLearningProfileRepository,
)


class AdaptiveLearningService:
    """Sits beside core grading — never replaces PASS/FAIL."""

    def __init__(self, exam_service: CoreExamService | None = None) -> None:
        self._exam = exam_service or CoreExamService()

    def process_check(
        self,
        db: Session,
        *,
        user_id: int,
        code: str,
        language_id: str,
        required: list[RequiredStructureSpec] | list[str] | list[dict],
        commit: bool = True,
    ) -> dict[str, Any]:
        exam = self._exam.examine(code, language_id, required)
        return self.process_exam_result(db, user_id=user_id, exam=exam, commit=commit)

    def process_exam_result(
        self,
        db: Session,
        *,
        user_id: int,
        exam: ExamResult,
        commit: bool = True,
    ) -> dict[str, Any]:
        repo = StudentLearningProfileRepository(db)
        profile = repo.get(user_id)
        apply_exam_to_profile(profile, exam)
        errors = analyze_errors(exam, profile)
        decision = decide_next_step(profile)
        apply_decision_to_profile(profile, decision)
        repo.save(profile)
        if commit:
            db.commit()
        return self._build_response(exam, profile, errors, decision)

    def get_profile(self, db: Session, user_id: int) -> dict[str, Any]:
        profile = StudentLearningProfileRepository(db).get(user_id)
        return {
            "profile": profile.to_dict(),
            "allowed_structures": get_allowed_structures_for_profile(profile),
        }

    @staticmethod
    def _build_response(
        exam: ExamResult,
        profile: StudentStructureProfile,
        errors: dict,
        decision: dict,
    ) -> dict[str, Any]:
        return {
            "exam": exam.to_dict(),
            "profile": profile.to_dict(),
            "error_analysis": errors,
            "adaptive": decision,
            "suggested_required": _suggested_required(profile, decision),
        }


def _suggested_required(profile: StudentStructureProfile, decision: dict) -> list[str]:
    focus = decision.get("focus_structures") or []
    if focus:
        return [str(item) for item in focus]
    return get_allowed_structures_for_profile(profile)
