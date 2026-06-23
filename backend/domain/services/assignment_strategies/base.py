from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from shared.enums import AssignmentType, DifficultyLevel


@dataclass(frozen=True)
class AssignmentCreationContext:
    teacher_id: int
    title: str
    description: str
    difficulty: DifficultyLevel
    languages: tuple[str, ...]
    payload: dict[str, Any]


class AssignmentCreationStrategy(ABC):
    assignment_type: AssignmentType

    @abstractmethod
    def validate(self, context: AssignmentCreationContext) -> None:
        """Raise ValueError when payload is invalid for this type."""

    @abstractmethod
    def expected_input_format(self) -> str:
        pass
