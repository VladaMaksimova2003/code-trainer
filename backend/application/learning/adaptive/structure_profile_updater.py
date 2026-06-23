"""Update StudentStructureProfile after a graded attempt."""
from __future__ import annotations

from domain.analysis.semantic_core import ExamResult
from domain.learning.learning_levels import WEAK_FAILURE_THRESHOLD
from domain.learning.skill_groups import CONCEPT_IDS
from domain.learning.student_structure_profile import StudentStructureProfile


def apply_exam_to_profile(profile: StudentStructureProfile, exam: ExamResult) -> None:
    detected = set(exam.core.detected)
    missing = set(exam.missing)

    for name in CONCEPT_IDS:
        if name in detected:
            profile.structures[name] = True

    for name in missing:
        if name not in CONCEPT_IDS:
            continue
        profile.failure_counts[name] = profile.failure_counts.get(name, 0) + 1
        if profile.failure_counts[name] >= WEAK_FAILURE_THRESHOLD:
            if name not in profile.weak_areas:
                profile.weak_areas.append(name)

    if exam.result == "PASS":
        profile.consecutive_passes += 1
    else:
        profile.consecutive_passes = 0

    profile.weak_areas = sorted(
        {
            name
            for name in profile.weak_areas
            if profile.failure_counts.get(name, 0) >= WEAK_FAILURE_THRESHOLD
        }
    )
