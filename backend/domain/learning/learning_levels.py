"""Level gates — deterministic, not ML."""
from __future__ import annotations

from domain.learning.skill_groups import CONCEPT_IDS

LearningLevel = str

LEVEL_BEGINNER = "beginner"
LEVEL_INTERMEDIATE = "intermediate"
LEVEL_ADVANCED = "advanced"

LEVEL_ORDER: tuple[str, ...] = (LEVEL_BEGINNER, LEVEL_INTERMEDIATE, LEVEL_ADVANCED)

LEVEL_STABILITY_REQUIREMENTS: dict[str, frozenset[str]] = {
    LEVEL_BEGINNER: frozenset({"loop", "function"}),
    LEVEL_INTERMEDIATE: frozenset({"loop", "function", "condition", "variable"}),
    LEVEL_ADVANCED: frozenset(CONCEPT_IDS),
}

WEAK_FAILURE_THRESHOLD = 2


def next_level(current: str) -> str | None:
    normalized = str(current or LEVEL_BEGINNER).strip().lower()
    if normalized not in LEVEL_ORDER:
        normalized = LEVEL_BEGINNER
    idx = LEVEL_ORDER.index(normalized)
    if idx + 1 >= len(LEVEL_ORDER):
        return None
    return LEVEL_ORDER[idx + 1]


def requirements_for_level(level: str) -> frozenset[str]:
    return LEVEL_STABILITY_REQUIREMENTS.get(
        str(level or LEVEL_BEGINNER).strip().lower(),
        LEVEL_STABILITY_REQUIREMENTS[LEVEL_BEGINNER],
    )
