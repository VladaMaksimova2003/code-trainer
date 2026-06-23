"""Seed must not overwrite tasks the teacher edited in the UI."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from application.curriculum.pascal.showcase.pascal_showcase_core import (
    find_showcase_task_by_slug,
    seed_pascal_v311_showcase_collection,
)
from application.curriculum.pascal.showcase.pascal_v311_showcase_all_specs import (
    all_pascal_v311_showcase_specs,
)
from application.tasks.services.teacher_assembly_preservation import (
    mark_teacher_assembly_override,
    should_skip_catalog_seed_refresh,
)
from infrastructure.db.models.base import Base
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.task.task import BlockReorderTask, Task as TaskModel
from infrastructure.db.models.task.task import TranslationTask
from infrastructure.db.models.task.task_curriculum_link import TaskCurriculumLinkModel


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


def test_seed_skips_refresh_when_teacher_override_set(db_session: Session):
    specs = all_pascal_v311_showcase_specs()
    chapter = "algo_basics"
    spec = specs[chapter][0]
    seed_pascal_v311_showcase_collection(db_session, chapter, (spec,))
    db_session.commit()

    row = find_showcase_task_by_slug(
        db_session, spec.slug, collection_key=chapter, curriculum_version="3.1.1"
    )
    assert row is not None
    row.title = "Правка преподавателя: линейный поиск"
    row.task_type = "debug_code"
    mark_teacher_assembly_override(row)
    db_session.commit()

    seed_pascal_v311_showcase_collection(db_session, chapter, (spec,))
    db_session.commit()

    refreshed = find_showcase_task_by_slug(
        db_session, spec.slug, collection_key=chapter, curriculum_version="3.1.1"
    )
    assert refreshed is not None
    assert refreshed.title == "Правка преподавателя: линейный поиск"
    assert refreshed.task_type == "debug_code"
    assert (refreshed.code_examples or {}).get("teacher_assembly_override") is True


def test_seed_skips_refresh_when_debug_codes_differ_without_override_flag(db_session: Session):
    specs = all_pascal_v311_showcase_specs()
    chapter = "algo_basics"
    debug_spec = next(spec for spec in specs[chapter] if spec.slug == "pas_005")
    seed_pascal_v311_showcase_collection(db_session, chapter, (debug_spec,))
    db_session.commit()

    row = find_showcase_task_by_slug(
        db_session, debug_spec.slug, collection_key=chapter, curriculum_version="3.1.1"
    )
    assert row is not None

    examples = dict(row.code_examples or {})
    showcase = dict(examples.get("curriculum_showcase") or {})
    showcase["primary_action"] = "debug"
    showcase["task_format"] = "исправление"
    showcase["starter_pascal"] = "program teacher_buggy;\nbegin\n  writeln('teacher edit');\nend."
    examples["pascal"] = "program teacher_fixed;\nbegin\n  writeln('teacher edit');\nend."
    examples["curriculum_showcase"] = showcase
    row.code_examples = examples
    row.title = "Правка преподавателя: подсчёт положительных"
    db_session.commit()

    assert should_skip_catalog_seed_refresh(row) is True

    seed_pascal_v311_showcase_collection(db_session, chapter, (debug_spec,))
    db_session.commit()

    refreshed = find_showcase_task_by_slug(
        db_session, debug_spec.slug, collection_key=chapter, curriculum_version="3.1.1"
    )
    assert refreshed is not None
    assert refreshed.title == "Правка преподавателя: подсчёт положительных"
    refreshed_showcase = dict((refreshed.code_examples or {}).get("curriculum_showcase") or {})
    assert "teacher edit" in str(refreshed_showcase.get("starter_pascal") or "")
    assert "teacher edit" in str((refreshed.code_examples or {}).get("pascal") or "")
