"""Python Course v1 showcase specs."""

from __future__ import annotations

from functools import lru_cache

from application.curriculum.python.catalog.python_curriculum_v3_catalog import slots_by_chapter
from application.curriculum.python.showcase.python_showcase_core import PythonShowcaseTaskSpec


@lru_cache(maxsize=1)
def all_python_v311_showcase_specs() -> dict[str, tuple[PythonShowcaseTaskSpec, ...]]:
    return {
        collection_key: tuple(slot.to_task_spec() for slot in slots)
        for collection_key, slots in slots_by_chapter().items()
    }


@lru_cache(maxsize=None)
def python_v311_showcase_specs_for_collection(
    collection_key: str,
) -> tuple[PythonShowcaseTaskSpec, ...]:
    from application.curriculum.python.catalog.python_curriculum_v3_catalog import slots_for_chapter

    return tuple(slot.to_task_spec() for slot in slots_for_chapter(collection_key))
