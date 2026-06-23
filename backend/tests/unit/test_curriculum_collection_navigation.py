"""Collection navigation crosses Pascal showcase chapters."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from application.curriculum.collections.curriculum_collection_navigation import build_collection_navigation
from application.curriculum.pascal.showcase.pascal_showcase_core import seed_pascal_showcase_collection
from application.curriculum.pascal.showcase.pascal_showcase_next import order_collection_showcase_tasks
from application.curriculum.pascal.showcase.pascal_v311_showcase_all_specs import all_pascal_v311_showcase_specs
from application.curriculum.pascal.showcase.pascal_v311_registry import (
    PASCAL_V311_SHOWCASE_COLLECTIONS,
    V311_CHAPTER_ORDER,
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
            BlockReorderTask.__table__,
            TaskCurriculumLinkModel.__table__,
        ],
    )
    session = sessionmaker(bind=engine)()
    try:
        specs = all_pascal_v311_showcase_specs()
        for col in PASCAL_V311_SHOWCASE_COLLECTIONS:
            if col.chapter_key in specs:
                seed_pascal_showcase_collection(session, col.chapter_key, specs[col.chapter_key])
        session.commit()
        yield session
    finally:
        session.close()


def test_last_task_in_first_chapter_links_to_next(db_session: Session):
    specs = all_pascal_v311_showcase_specs()
    first_key, second_key = V311_CHAPTER_ORDER[0], V311_CHAPTER_ORDER[1]
    ordered_first = order_collection_showcase_tasks(db_session, first_key, specs[first_key])
    ordered_second = order_collection_showcase_tasks(db_session, second_key, specs[second_key])
    last_first = int(ordered_first[-1]["task_id"])
    nav = build_collection_navigation(
        db_session,
        language="pascal",
        chapter_key=first_key,
        task_id=last_first,
    )
    assert nav is not None
    assert nav["next_task_id"] == int(ordered_second[0]["task_id"])
    assert nav["next_collection_id"] == f"pascal_{second_key}_v311"
    assert nav["course_completed"] is False


def test_last_task_in_final_chapter_marks_course_completed(db_session: Session):
    specs = all_pascal_v311_showcase_specs()
    final_key = V311_CHAPTER_ORDER[-1]
    ordered = order_collection_showcase_tasks(db_session, final_key, specs[final_key])
    nav = build_collection_navigation(
        db_session,
        language="pascal",
        chapter_key=final_key,
        task_id=int(ordered[-1]["task_id"]),
    )
    assert nav is not None
    assert nav["next_task_id"] is None
    assert nav["course_completed"] is True
