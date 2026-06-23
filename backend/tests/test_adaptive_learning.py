"""Adaptive learning layer — isolated from core PASS/FAIL."""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from application.analysis.core.educational_validator import EducationalValidator
from application.learning.adaptive.adaptive_learning_engine import AdaptiveLearningEngine
from application.learning.adaptive.adaptive_learning_service import AdaptiveLearningService
from application.learning.adaptive.error_analysis import analyze_errors
from application.learning.adaptive.structure_profile_updater import apply_exam_to_profile
from domain.learning.student_structure_profile import StudentStructureProfile
from infrastructure.db.models.base import Base
from infrastructure.db.models.learning.student_learning_profile import (
    StudentLearningProfileModel,
)


def test_profile_marks_detected_true():
    exam = EducationalValidator().validate(
        "def f(n):\n    for i in range(n):\n        if i % 2:\n            return i\n",
        "python",
        ["loop", "function"],
    )
    profile = StudentStructureProfile.empty(user_id=1)
    apply_exam_to_profile(profile, exam)
    assert profile.structures["loop"] is True
    assert profile.structures["function"] is True


def test_error_analysis_on_fail():
    exam = EducationalValidator().validate("print(1)\n", "python", ["loop"])
    profile = StudentStructureProfile.empty(user_id=1)
    apply_exam_to_profile(profile, exam)
    analysis = analyze_errors(exam, profile)
    assert "loop" in analysis["missing"]
    assert analysis["weakest_structure"] == "loop"
    assert "loop" in analysis["recommendation"] or "repeat" in analysis["recommendation"]


def test_adaptive_upgrade_after_stable_passes():
    profile = StudentStructureProfile.empty(user_id=1)
    profile.structures["loop"] = True
    profile.structures["function"] = True
    profile.consecutive_passes = 2
    decision = AdaptiveLearningEngine().decide_next_step(profile)
    assert decision["action"] == "upgrade_level"
    assert decision["next_level"] == "intermediate"


def test_adaptive_repeat_on_weak_area():
    profile = StudentStructureProfile.empty(user_id=1)
    profile.weak_areas = ["variable"]
    profile.failure_counts["variable"] = 3
    decision = AdaptiveLearningEngine().decide_next_step(profile)
    assert decision["action"] == "repeat_level"
    assert "variable" in decision["focus_structures"]


def test_process_exam_persists_profile():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine, tables=[StudentLearningProfileModel.__table__])
    session = sessionmaker(bind=engine)()
    exam = EducationalValidator().validate(
        "while True:\n    break\n",
        "python",
        ["loop"],
    )
    payload = AdaptiveLearningService().process_exam_result(
        session,
        user_id=42,
        exam=exam,
        commit=True,
    )
    assert payload["exam"]["result"] == "PASS"
    assert payload["profile"]["structures"]["loop"] is True
    assert "adaptive" in payload
    assert "error_analysis" in payload
