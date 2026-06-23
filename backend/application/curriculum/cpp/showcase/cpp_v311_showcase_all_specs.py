"""Build showcase specs for C++ Course v1."""

from __future__ import annotations

from functools import lru_cache

from application.curriculum.cpp.catalog.cpp_curriculum_v3_catalog import (
    all_v311_task_records,
    record_to_spec_dict,
    records_by_chapter,
)


def all_cpp_v311_showcase_specs() -> dict[str, tuple[dict, ...]]:
    grouped = records_by_chapter()
    return {key: tuple(record_to_spec_dict(r) for r in grouped[key]) for key in grouped}


@lru_cache(maxsize=None)
def cpp_v311_showcase_specs_for_collection(chapter_key: str) -> tuple[dict, ...]:
    key = str(chapter_key or "").strip()
    return tuple(
        record_to_spec_dict(rec)
        for rec in all_v311_task_records()
        if rec.chapter_key == key
    )


def specs_for_chapters(chapters: tuple[str, ...]) -> dict[str, tuple[dict, ...]]:
    all_specs = all_cpp_v311_showcase_specs()
    return {key: all_specs[key] for key in chapters if key in all_specs}


def all_cpp_v311_task_records():
    return all_v311_task_records()
