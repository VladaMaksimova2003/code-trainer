"""Tests for Pascal Course v3.1.1 catalog, builders, and seed."""

from __future__ import annotations

import re

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from application.curriculum.pascal.catalog.pascal_curriculum_v3_catalog import (
    V311_TOTAL_TASKS,
    all_v311_slots,
    all_v311_task_records,
    catalog_summary,
    validate_v311_catalog,
)
from application.curriculum.pascal.catalog.pascal_known_language import validate_variants
from application.curriculum.pascal.catalog.pascal_v311_builder_mapping import (
    TASK_FORMAT_TO_BUILDER,
    builder_for_task_format,
)
from application.curriculum.pascal.showcase.pascal_showcase_core import (
    PascalShowcaseTaskSpec,
    _BUILDERS,
    find_showcase_task_by_slug,
    list_showcase_tasks_for_collection,
    seed_pascal_v311_showcase_collection,
)
from application.curriculum.pascal.showcase.pascal_v311_registry import (
    PASCAL_V311_SHOWCASE_COLLECTIONS,
    V311_CHAPTER_ORDER,
    V311_COLLECTION_TARGETS,
)
from application.curriculum.pascal.showcase.pascal_v311_showcase_all_specs import (
    all_pascal_v311_showcase_specs,
)
from application.curriculum.collections.curriculum_collections_registry import (
    list_curriculum_collections,
)
from infrastructure.db.models.base import Base
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.task.task import BlockReorderTask, Task as TaskModel
from infrastructure.db.models.task.task import TranslationTask
from infrastructure.db.models.task.task_curriculum_link import TaskCurriculumLinkModel

LANG_PATTERN = re.compile(r"python|c#|csharp|java", re.I)


@pytest.fixture
def db_session() -> Session:
    load_models()
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            TaskModel.__table__,
            TranslationTask.__table__,
            BlockReorderTask.__table__,            TaskCurriculumLinkModel.__table__,
        ],
    )
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


def test_pascal_v311_catalog_count():
    records = all_v311_task_records()
    assert len(records) == V311_TOTAL_TASKS
    assert len(V311_CHAPTER_ORDER) == len(PASCAL_V311_SHOWCASE_COLLECTIONS)
    assert sum(V311_COLLECTION_TARGETS.values()) == V311_TOTAL_TASKS
    errors = validate_v311_catalog()
    assert errors == [], errors


def test_pascal_v311_no_analyze():
    for rec in all_v311_task_records():
        assert rec.primary_action != "analyze"
        assert rec.task_format != "сопоставление"


def test_pascal_v311_language_neutral_metadata():
    for rec in all_v311_task_records():
        for value in (rec.title, rec.educational_goal, rec.chapter_title):
            assert not LANG_PATTERN.search(value), f"{rec.slot_id}: {value}"


def test_pascal_v311_all_patterns_have_builders():
    missing: list[str] = []
    for rec in all_v311_task_records():
        try:
            builder = builder_for_task_format(rec.task_format)
        except KeyError:
            missing.append(rec.slot_id)
            continue
        if builder not in _BUILDERS:
            missing.append(f"{rec.slot_id}:{builder}")
    assert missing == []


def test_pascal_v311_collections_registered():
    assert len(PASCAL_V311_SHOWCASE_COLLECTIONS) == len(V311_CHAPTER_ORDER)
    registered_ids = {c.collection_id for c in list_curriculum_collections()}
    for col in PASCAL_V311_SHOWCASE_COLLECTIONS:
        assert col.collection_id in registered_ids


def test_translation_snippet_builder(db_session: Session):
    specs = all_pascal_v311_showcase_specs()
    snippet_specs = [
        s
        for s in specs["algo_basics"]
        if s.builder_key == "translation_to_pascal"
    ]
    assert snippet_specs, "expected at least one translation task in algo_basics"
    spec = snippet_specs[0]
    report = seed_pascal_v311_showcase_collection(
        db_session, "algo_basics", (spec,)
    )
    db_session.commit()
    assert report.errors == [], report.errors
    row = find_showcase_task_by_slug(
        db_session, spec.slug, collection_key="algo_basics", curriculum_version="3.1.1"
    )
    assert row is not None
    assert row.task_type == spec.assignment_type
    showcase = (row.code_examples or {}).get("curriculum_showcase") or {}
    assert showcase.get("curriculum_version") == "3.1.1"
    assert "python" in (row.code_examples or {})


def test_pascal_v311_all_tasks_have_known_language():
    missing: list[str] = []
    for slot in all_v311_slots():
        extra = slot.extra or {}
        variants = extra.get("known_language_variants")
        if not variants:
            missing.append(slot.slot_id)
            continue
        if validate_variants(variants):
            missing.append(slot.slot_id)
    assert missing == []


def test_debug_task_has_known_language(db_session: Session):
    specs = all_pascal_v311_showcase_specs()
    debug_specs = [s for s in specs["algo_basics"] if s.builder_key == "pascal_debug_starter"]
    assert debug_specs
    spec = debug_specs[0]
    report = seed_pascal_v311_showcase_collection(db_session, "algo_basics", (spec,))
    db_session.commit()
    assert report.errors == [], report.errors
    row = find_showcase_task_by_slug(
        db_session, spec.slug, collection_key="algo_basics", curriculum_version="3.1.1"
    )
    assert row is not None
    assert "python" in (row.code_examples or {})


def test_seed_pascal_v311_idempotent(db_session: Session):
    specs = all_pascal_v311_showcase_specs()
    key = "algo_basics"
    first = seed_pascal_v311_showcase_collection(db_session, key, specs[key])
    db_session.commit()
    assert first.errors == [], first.errors
    created_first = len(first.created)

    second = seed_pascal_v311_showcase_collection(db_session, key, specs[key])
    db_session.commit()
    assert second.errors == [], second.errors
    assert len(second.created) == 0
    assert created_first == len(specs[key])

    rows = list_showcase_tasks_for_collection(db_session, key, curriculum_version="3.1.1")
    assert len(rows) == len(specs[key])


def test_pascal_v311_full_seed_all_chapters(db_session: Session):
    specs = all_pascal_v311_showcase_specs()
    all_errors: list[str] = []
    for col in PASCAL_V311_SHOWCASE_COLLECTIONS:
        report = seed_pascal_v311_showcase_collection(
            db_session, col.chapter_key, specs[col.chapter_key]
        )
        all_errors.extend(report.errors)
    db_session.commit()
    assert all_errors == [], all_errors
    total = sum(
        len(
            list_showcase_tasks_for_collection(
                db_session, col.chapter_key, curriculum_version="3.1.1"
            )
        )
        for col in PASCAL_V311_SHOWCASE_COLLECTIONS
    )
    assert total == V311_TOTAL_TASKS


def test_pascal_v311_catalog_summary():
    summary = catalog_summary()
    assert summary["total_tasks"] == V311_TOTAL_TASKS
    assert summary["chapters"] == len(V311_CHAPTER_ORDER)
    assert set(summary["builder_counts"]) <= set(_BUILDERS)
    assert set(summary["format_counts"]) <= set(TASK_FORMAT_TO_BUILDER)
