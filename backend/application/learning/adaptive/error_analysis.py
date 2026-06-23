"""Post-check error analysis from ExamResult (no core changes)."""
from __future__ import annotations

from domain.analysis.semantic_core import ExamResult
from domain.learning.student_structure_profile import StudentStructureProfile
from infrastructure.analysis.concept_ast_detector import concept_label


def analyze_errors(
    exam: ExamResult,
    profile: StudentStructureProfile,
) -> dict:
    missing = list(exam.missing)
    failure_counts = profile.failure_counts
    ranked = sorted(
        failure_counts.items(),
        key=lambda item: (-item[1], item[0]),
    )
    weakest = missing[0] if missing else (ranked[0][0] if ranked and ranked[0][1] > 0 else None)

    frequent = [
        name
        for name, count in ranked
        if count >= 1 and name in missing
    ][:3]
    if not frequent and ranked:
        frequent = [name for name, count in ranked if count > 0][:3]

    recommendation = _recommendation(weakest, exam.result)
    return {
        "missing": missing,
        "most_frequent_failures": frequent,
        "weakest_structure": weakest,
        "recommendation": recommendation,
        "result": exam.result,
    }


def _recommendation(weakest: str | None, result: str) -> str:
    if result == "PASS":
        return "continue_current_level"
    if weakest:
        return f"repeat exercises with {concept_label(weakest)}"
    return "review_required_structures"
