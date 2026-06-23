from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from shared.enums import AssignmentType, DifficultyLevel


@dataclass(frozen=True)
class CreateAssignmentCommand:
    teacher_id: int
    assignment_type: AssignmentType
    difficulty: DifficultyLevel
    languages: list[str]
    title: str
    description: str
    payload: dict[str, Any] = field(default_factory=dict)
    patterns: list[str] = field(default_factory=list)
    test_cases: list[dict[str, Any]] = field(default_factory=list)
