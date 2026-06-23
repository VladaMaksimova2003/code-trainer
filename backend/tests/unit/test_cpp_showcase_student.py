"""C++ showcase student view returns subtopics for the frontend."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from application.curriculum.cpp.showcase.cpp_showcase_core import seed_cpp_collection
from application.curriculum.cpp.showcase.cpp_showcase_student import build_cpp_showcase_student_view
from application.curriculum.cpp.showcase.cpp_v311_showcase_all_specs import all_cpp_v311_showcase_specs
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
        specs = all_cpp_v311_showcase_specs()
        seed_cpp_collection(session, "algo_basics", specs["algo_basics"])
        session.commit()
        yield session
    finally:
        session.close()


def test_cpp_action_labels_are_cpp_specific():
    from application.curriculum.display.curriculum_labels import (
        get_action_description_ru,
        get_action_skill_label,
    )

    assert "C++" in get_action_skill_label("translate", language="cpp")
    assert "Pascal" not in get_action_skill_label("translate", language="cpp")
    assert "C++" in get_action_description_ru("translate", language="cpp")


def test_cpp_showcase_student_view_exposes_subtopics(db_session: Session):
    view = build_cpp_showcase_student_view(db_session, "algo_basics", user_id=None)
    subtopics = view.get("subtopics") or []
    assert subtopics, "expected subtopics for C++ showcase student view"
    assert view.get("total_tasks", 0) > 0
    assert sum(len(section.get("tasks") or []) for section in subtopics) == view["total_tasks"]
    first_task = subtopics[0]["tasks"][0]
    assert first_task.get("task_id")
    assert first_task.get("title")
    assert "Pascal" not in (first_task.get("action_skill_label") or "")
