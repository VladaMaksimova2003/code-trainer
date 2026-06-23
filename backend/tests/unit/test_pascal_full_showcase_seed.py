"""Seed all Pascal showcase collections in memory."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from application.curriculum.pascal.showcase.pascal_showcase_all_specs import all_pascal_showcase_specs
from application.curriculum.pascal.showcase.pascal_showcase_core import (
    list_showcase_tasks_for_collection,
    seed_pascal_showcase_collection,
)
from application.curriculum.pascal.showcase.pascal_showcase_registry import PASCAL_SHOWCASE_COLLECTIONS
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


def test_all_collections_seed_without_errors(db_session: Session):
    specs = all_pascal_showcase_specs()
    assert len(specs) == len(PASCAL_SHOWCASE_COLLECTIONS)
    all_errors: list[str] = []
    for col in PASCAL_SHOWCASE_COLLECTIONS:
        key = col.chapter_key
        report = seed_pascal_showcase_collection(db_session, key, specs[key])
        all_errors.extend(report.errors)
    db_session.commit()
    assert all_errors == [], all_errors


def test_total_showcase_task_count(db_session: Session):
    specs = all_pascal_showcase_specs()
    for col in PASCAL_SHOWCASE_COLLECTIONS:
        seed_pascal_showcase_collection(db_session, col.chapter_key, specs[col.chapter_key])
    db_session.commit()
    total = sum(
        len(list_showcase_tasks_for_collection(db_session, col.chapter_key))
        for col in PASCAL_SHOWCASE_COLLECTIONS
    )
    assert total == sum(len(specs[k]) for k in specs)
    assert total == 102

