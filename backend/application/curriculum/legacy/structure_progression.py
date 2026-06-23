"""Hardcoded learning progression — does NOT affect PASS/FAIL grading."""
from __future__ import annotations

from domain.analysis.semantic_core import CORE_STRUCTURE_IDS

# difficulty level → subtype id
STRUCTURE_PROGRESSION: dict[str, dict[int, str]] = {
    "function": {1: "function", 2: "method", 3: "lambda"},
    "loop": {1: "for_loop", 2: "while_loop", 3: "nested_loop"},
    "call": {1: "call", 2: "method_call", 3: "chained_call"},
}

MAX_CURRICULUM_LEVEL = 3


def get_allowed_structures(level: int) -> list[str]:
    """Core structure ids + subtype tags unlocked at or below level."""
    level = max(1, min(int(level), MAX_CURRICULUM_LEVEL))
    allowed: set[str] = set()
    for structure, steps in STRUCTURE_PROGRESSION.items():
        for step_level, subtype in steps.items():
            if step_level <= level:
                allowed.add(structure)
                allowed.add(subtype)
    for core_id in CORE_STRUCTURE_IDS:
        if core_id not in STRUCTURE_PROGRESSION and level >= 1:
            allowed.add(core_id)
    return sorted(allowed)


def get_next_structure(current_level: int) -> dict[str, str]:
    """Subtype introduced at current_level + 1 per structure family."""
    next_level = int(current_level) + 1
    unlocked: dict[str, str] = {}
    for structure, steps in STRUCTURE_PROGRESSION.items():
        subtype = steps.get(next_level)
        if subtype is not None:
            unlocked[structure] = subtype
    return unlocked


def is_structure_allowed(name: str, level: int) -> bool:
    tag = str(name).strip().lower()
    return tag in get_allowed_structures(level)


def get_level_plan(level: int) -> dict:
    level = max(1, min(int(level), MAX_CURRICULUM_LEVEL))
    allowed = get_allowed_structures(level)
    next_unlock = list(get_next_structure(level).values())
    return {
        "level": level,
        "allowed_structures": allowed,
        "next_unlock": next_unlock,
    }
