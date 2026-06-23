"""Unified Pascal showcase specs — curriculum v2 pedagogical slots."""

from __future__ import annotations

from application.curriculum.pascal.catalog.pascal_curriculum_v2_catalog import slots_by_collection
from application.curriculum.pascal.showcase.pascal_showcase_core import PascalShowcaseTaskSpec


def all_pascal_showcase_specs() -> dict[str, tuple[PascalShowcaseTaskSpec, ...]]:
    return {
        collection_key: tuple(slot.to_task_spec() for slot in slots)
        for collection_key, slots in slots_by_collection().items()
    }


