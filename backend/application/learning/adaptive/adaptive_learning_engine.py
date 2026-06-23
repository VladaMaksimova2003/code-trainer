"""Level and focus decisions — does not affect PASS/FAIL."""
from __future__ import annotations

from domain.learning.learning_levels import (
    LEVEL_BEGINNER,
    LEVEL_ORDER,
    next_level,
    requirements_for_level,
)
from domain.learning.student_structure_profile import StudentStructureProfile


def decide_next_step(profile: StudentStructureProfile) -> dict:
    current = profile.learning_level or LEVEL_BEGINNER
    required = requirements_for_level(current)
    stable = _is_stable(profile, required)
    weakest = profile.weak_areas[0] if profile.weak_areas else _pick_weakest(profile)

    if not stable:
        return {
            "action": "repeat_level",
            "current_level": current,
            "next_level": current,
            "focus_structures": profile.weak_areas or ([weakest] if weakest else []),
            "reason": "weak_or_missing_structures",
        }

    upgraded = next_level(current)
    if upgraded and profile.consecutive_passes >= 2:
        return {
            "action": "upgrade_level",
            "current_level": current,
            "next_level": upgraded,
            "focus_structures": list(requirements_for_level(upgraded)),
            "reason": "stable_profile",
        }

    return {
        "action": "same_level",
        "current_level": current,
        "next_level": current,
        "focus_structures": list(required),
        "reason": "building_stability",
    }


def apply_decision_to_profile(
    profile: StudentStructureProfile,
    decision: dict,
) -> None:
    if decision.get("action") == "upgrade_level":
        profile.learning_level = str(decision.get("next_level") or profile.learning_level)


def _is_stable(profile: StudentStructureProfile, required: frozenset[str]) -> bool:
    for name in required:
        if not profile.structures.get(name, False):
            return False
        if profile.failure_counts.get(name, 0) >= 2:
            return False
    return True


def _pick_weakest(profile: StudentStructureProfile) -> str | None:
    if not profile.failure_counts:
        return None
    name, _ = max(profile.failure_counts.items(), key=lambda item: (item[1], item[0]))
    return name if profile.failure_counts.get(name, 0) > 0 else None


class AdaptiveLearningEngine:
    """Rule-based level and focus decisions."""

    def decide_next_step(self, profile: StudentStructureProfile) -> dict:
        return decide_next_step(profile)

    def apply_decision(self, profile: StudentStructureProfile, decision: dict) -> None:
        apply_decision_to_profile(profile, decision)

    def allowed_structures(self, profile: StudentStructureProfile) -> list[str]:
        return get_allowed_structures_for_profile(profile)


def get_allowed_structures_for_profile(profile: StudentStructureProfile) -> list[str]:
    level = profile.learning_level or LEVEL_BEGINNER
    if level not in LEVEL_ORDER:
        level = LEVEL_BEGINNER
    return sorted(requirements_for_level(level))
