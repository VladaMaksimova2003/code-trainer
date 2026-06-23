"""Pedagogical slot model for Python Course v1."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from application.curriculum.python.showcase.python_showcase_core import PythonShowcaseTaskSpec

RECOGNIZE_ACTION = "recognize"
PRIMARY_ACTIONS = frozenset({"translate", "assemble", "analyze", "debug", "implement"})


@dataclass(frozen=True)
class PedagogicalSlotSpec:
    slot_id: str
    collection_key: str
    target_tc: str
    primary_action: str
    title_suffix: str
    short_instruction: str
    description: str
    difficulty: str
    exercise_pattern_id: str
    assignment_type: str
    builder_key: str
    secondary_actions: tuple[str, ...] = ()
    extra: dict[str, Any] | None = None
    slug: str | None = None

    def __post_init__(self) -> None:
        if self.primary_action not in PRIMARY_ACTIONS:
            raise ValueError(f"Invalid primary_action: {self.primary_action}")

    @property
    def collection_id(self) -> str:
        return f"python_{self.collection_key}_v311"

    @property
    def task_slug(self) -> str:
        return self.slug or self.slot_id

    @property
    def technical_concept_id(self) -> str:
        return self.target_tc

    def to_task_spec(self) -> PythonShowcaseTaskSpec:
        return PythonShowcaseTaskSpec(
            collection_key=self.collection_key,
            slug=self.task_slug,
            title_suffix=self.title_suffix,
            description=self.description,
            difficulty=self.difficulty,
            technical_concept_id=self.target_tc,
            exercise_pattern_id=self.exercise_pattern_id,
            assignment_type=self.assignment_type,
            builder_key=self.builder_key,
            extra=self.extra,
            slot_id=self.slot_id,
            primary_action=self.primary_action,
            secondary_actions=self.secondary_actions,
            short_instruction=self.short_instruction,
        )

    def with_extra(self, **updates: Any) -> PedagogicalSlotSpec:
        merged = dict(self.extra or {})
        merged.update(updates)
        return replace(self, extra=merged)
