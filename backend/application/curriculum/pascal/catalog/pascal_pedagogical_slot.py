"""Pedagogical slot model — one slot = one showcase task (curriculum v2)."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Any

from application.curriculum.pascal.showcase.pascal_showcase_core import PascalShowcaseTaskSpec
from application.curriculum.pascal.showcase.pascal_showcase_registry import collection_by_key

RECOGNIZE_ACTION = "recognize"
PRIMARY_ACTIONS = frozenset(
    {"translate", "assemble", "analyze", "debug", "implement"}
)


@dataclass(frozen=True)
class PedagogicalSlotSpec:
    """One pedagogical slot → one seeded task."""

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
        if RECOGNIZE_ACTION in self.secondary_actions and len(self.secondary_actions) > 3:
            raise ValueError("Too many secondary_actions")
        for action in self.secondary_actions:
            if action == self.primary_action:
                raise ValueError("primary_action must not appear in secondary_actions")
            if action != RECOGNIZE_ACTION and action not in PRIMARY_ACTIONS:
                raise ValueError(f"Invalid secondary_action: {action}")

    @property
    def collection_id(self) -> str:
        col = collection_by_key(self.collection_key)
        if col is None:
            return f"pascal_{self.collection_key}_showcase"
        return col.collection_id

    @property
    def task_slug(self) -> str:
        return self.slug or self.slot_id

    @property
    def technical_concept_id(self) -> str:
        return self.target_tc

    def to_task_spec(self) -> PascalShowcaseTaskSpec:
        return PascalShowcaseTaskSpec(
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


def showcase_meta_from_slot(slot: PedagogicalSlotSpec, *, exercise_pattern_id: str) -> dict[str, Any]:
    return {
        "group": _effective_group(slot.collection_key),
        "collection_key": slot.collection_key,
        "collection_id": slot.collection_id,
        "slot_id": slot.slot_id,
        "slug": slot.task_slug,
        "technical_concept_id": slot.target_tc,
        "target_tc": slot.target_tc,
        "exercise_pattern_id": exercise_pattern_id,
        "primary_action": slot.primary_action,
        "secondary_actions": list(slot.secondary_actions),
        "short_instruction": slot.short_instruction,
        "curriculum_version": 2,
    }


def _effective_group(collection_key: str) -> str:
    from application.curriculum.pascal.showcase.pascal_showcase_registry import effective_showcase_group

    return effective_showcase_group(collection_key)

