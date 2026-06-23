"""Tests - Pascal conditions curriculum showcase seed."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from application.curriculum.pascal.legacy.conditions.conditions_showcase_data import conditions_showcase_specs
from application.curriculum.pascal.legacy.conditions.conditions_showcase_seeder import (
    find_showcase_task_by_slug,
    list_showcase_tasks,
    seed_pascal_conditions_showcase,
)
from application.curriculum.pascal.legacy.loops.loops_showcase_seeder import seed_pascal_loops_showcase
from application.curriculum.task_curriculum_link_service import (
    TaskCurriculumLinkService,
    validate_task_curriculum_link_metadata,
)
from domain.learning.curriculum.task_link_exceptions import TaskCurriculumLinkValidationError
from infrastructure.db.models.base import Base
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.task.task import BlockReorderTask, Task as TaskModel
from infrastructure.db.models.task.task import TranslationTask
from infrastructure.db.models.task.task_curriculum_link import TaskCurriculumLinkModel
from infrastructure.db.models.user.user import User


@pytest.fixture
def db_session() -> Session:
    load_models()
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
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


def test_seed_creates_showcase_tasks_with_primary_links(db_session: Session):
    report = seed_pascal_conditions_showcase(db_session)
    db_session.commit()

    assert report.errors == []
    assert len(report.created) == len(conditions_showcase_specs())
    assert len(report.linked) == len(conditions_showcase_specs())

    tasks = list_showcase_tasks(db_session)
    assert len(tasks) == 6
    for item in tasks:
        assert item["has_primary_link"] is True
        assert item["learning_concept_id"] == "conditions"
        assert item["action"]
        assert item["exercise_pattern_id"]
        assert item["technical_concept_id"]


def test_seed_is_idempotent(db_session: Session):
    first = seed_pascal_conditions_showcase(db_session)
    db_session.commit()
    second = seed_pascal_conditions_showcase(db_session)
    db_session.commit()

    assert len(first.created) == 6
    assert second.created == []
    assert len(second.skipped) >= 6
    assert len(list_showcase_tasks(db_session)) == 6


def test_conditions_seed_does_not_touch_loops(db_session: Session):
    seed_pascal_loops_showcase(db_session)
    db_session.commit()
    loops_before = len(
        __import__(
            "application.curriculum.pascal.legacy.loops.loops_showcase_seeder",
            fromlist=["list_showcase_tasks"],
        ).list_showcase_tasks(db_session)
    )

    seed_pascal_conditions_showcase(db_session)
    db_session.commit()

    loops_after = len(
        __import__(
            "application.curriculum.pascal.legacy.loops.loops_showcase_seeder",
            fromlist=["list_showcase_tasks"],
        ).list_showcase_tasks(db_session)
    )
    assert loops_before == loops_after == 7
    assert len(list_showcase_tasks(db_session)) == 6


def test_each_showcase_task_link_metadata(db_session: Session):
    seed_pascal_conditions_showcase(db_session)
    db_session.commit()
    svc = TaskCurriculumLinkService(db_session)

    for spec in conditions_showcase_specs():
        task = find_showcase_task_by_slug(db_session, spec.slug)
        assert task is not None
        meta = svc.get_task_curriculum_metadata(task.id)
        primary = meta["primary_link"]
        assert primary is not None
        assert primary["technical_concept_id"] == spec.technical_concept_id
        assert primary["exercise_pattern_id"] == spec.exercise_pattern_id
        assert primary["learning_concept_id"] == "conditions"
        assert primary["action"] == validate_task_curriculum_link_metadata(
            "pascal",
            spec.technical_concept_id,
            spec.exercise_pattern_id,
        )["action"]


def test_invalid_conditions_link_rejected():
    with pytest.raises(TaskCurriculumLinkValidationError, match="not allowed"):
        validate_task_curriculum_link_metadata(
            "pascal",
            "simple_branch",
            "dbg_pascal_logic_fix",
        )

