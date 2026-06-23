"""Pascal Course v3.1.1 showcase specs — 18 chapters, 200 tasks."""

from __future__ import annotations

from functools import lru_cache

from application.curriculum.pascal.catalog.pascal_curriculum_v3_catalog import slots_by_chapter
from application.curriculum.pascal.showcase.pascal_showcase_core import PascalShowcaseTaskSpec


@lru_cache(maxsize=1)
def all_pascal_v311_showcase_specs() -> dict[str, tuple[PascalShowcaseTaskSpec, ...]]:
    return {
        collection_key: tuple(slot.to_task_spec() for slot in slots)
        for collection_key, slots in slots_by_chapter().items()
    }


@lru_cache(maxsize=None)
def pascal_v311_showcase_specs_for_collection(
    collection_key: str,
) -> tuple[PascalShowcaseTaskSpec, ...]:
    from application.curriculum.pascal.catalog.pascal_curriculum_v3_catalog import slots_for_chapter

    return tuple(slot.to_task_spec() for slot in slots_for_chapter(collection_key))
