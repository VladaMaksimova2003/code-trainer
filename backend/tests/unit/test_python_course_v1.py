"""Tests for Python Course v1.2 catalog and registry."""

from __future__ import annotations

import re

from application.curriculum.python.catalog.python_curriculum_v3_catalog import (
    V311_TOTAL_TASKS,
    all_v311_task_records,
    catalog_summary,
    validate_v311_catalog,
)
from application.curriculum.python.showcase.python_v311_registry import (
    PYTHON_V311_SHOWCASE_COLLECTIONS,
    V311_CHAPTER_ORDER,
    V311_COLLECTION_TARGETS,
)

LANG_PATTERN = re.compile(r"pascal|c#|csharp|java|c\+\+", re.I)


def test_python_v12_catalog_count():
    records = all_v311_task_records()
    assert len(records) == V311_TOTAL_TASKS
    assert len(V311_CHAPTER_ORDER) == len(PYTHON_V311_SHOWCASE_COLLECTIONS)
    assert sum(V311_COLLECTION_TARGETS.values()) == V311_TOTAL_TASKS
    errors = validate_v311_catalog()
    assert errors == [], errors


def test_python_v12_no_analyze():
    for rec in all_v311_task_records():
        assert rec.primary_action != "analyze"
        assert rec.task_format != "сопоставление"


def test_python_v12_language_neutral_metadata():
    for rec in all_v311_task_records():
        for value in (rec.title, rec.educational_goal, rec.chapter_title):
            assert not LANG_PATTERN.search(value), f"{rec.slot_id}: {value}"


def test_python_v12_collections_registered():
    assert len(PYTHON_V311_SHOWCASE_COLLECTIONS) == len(V311_CHAPTER_ORDER)
    keys = {c.chapter_key for c in PYTHON_V311_SHOWCASE_COLLECTIONS}
    assert "algo_basics" in keys
    assert "inheritance_capstone" in keys


def test_python_v12_catalog_summary():
    summary = catalog_summary()
    assert summary["total_tasks"] == V311_TOTAL_TASKS
    assert summary["chapters"] == len(V311_CHAPTER_ORDER)
