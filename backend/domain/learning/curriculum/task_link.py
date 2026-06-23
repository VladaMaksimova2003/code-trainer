"""Task curriculum link domain record."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class TaskCurriculumLink:
    id: int
    task_id: int
    language: str
    learning_concept_id: str
    technical_concept_id: str
    exercise_pattern_id: str
    action: str
    is_primary: bool
    created_at: datetime | None = None
