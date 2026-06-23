"""Tests — Pascal loops curriculum showcase seed."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from application.curriculum.pascal.legacy.loops.loops_showcase_data import (
    loops_showcase_specs,
)
from application.curriculum.pascal.legacy.loops.loops_showcase_seeder import (
    find_showcase_task_by_slug,
    list_showcase_tasks,
    seed_pascal_loops_showcase,
)
from application.curriculum.task_curriculum_link_service import (
    TaskCurriculumLinkService,
    validate_task_curriculum_link_metadata,
)
from application.tasks.services.catalog.task_query import TaskQueryService
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
    report = seed_pascal_loops_showcase(db_session)
    db_session.commit()

    assert report.errors == []
    assert len(report.created) == len(loops_showcase_specs())
    assert len(report.linked) == len(loops_showcase_specs())

    tasks = list_showcase_tasks(db_session)
    assert len(tasks) == 7
    for item in tasks:
        assert item["has_primary_link"] is True
        assert item["learning_concept_id"] == "loops"
        assert item["action"]
        assert item["exercise_pattern_id"]
        assert item["technical_concept_id"]


def test_seed_is_idempotent(db_session: Session):
    first = seed_pascal_loops_showcase(db_session)
    db_session.commit()
    second = seed_pascal_loops_showcase(db_session)
    db_session.commit()

    assert len(first.created) == 7
    assert second.created == []
    assert len(second.skipped) >= 7
    assert len(list_showcase_tasks(db_session)) == 7


def test_each_showcase_task_link_metadata(db_session: Session):
    seed_pascal_loops_showcase(db_session)
    db_session.commit()
    svc = TaskCurriculumLinkService(db_session)

    for spec in loops_showcase_specs():
        task = find_showcase_task_by_slug(db_session, spec.slug)
        assert task is not None
        meta = svc.get_task_curriculum_metadata(task.id)
        primary = meta["primary_link"]
        assert primary is not None
        assert primary["technical_concept_id"] == spec.technical_concept_id
        assert primary["exercise_pattern_id"] == spec.exercise_pattern_id
        assert primary["learning_concept_id"] == "loops"
        assert primary["action"] == validate_task_curriculum_link_metadata(
            "pascal",
            spec.technical_concept_id,
            spec.exercise_pattern_id,
        )["action"]


def test_invalid_showcase_link_rejected():
    with pytest.raises(TaskCurriculumLinkValidationError, match="disabled"):
        validate_task_curriculum_link_metadata(
            "pascal",
            "loop_control",
            "asm_flowchart_to_blocks",
        )


def test_legacy_task_without_link_still_loadable(db_session: Session):
    legacy = TaskModel(
        title="Legacy task without curriculum",
        description="unchanged",
        task_type="task_translate_snippet",
        difficulty="easy",
        test_cases=[],
        code_examples={},
        flow_spec={},
    )
    db_session.add(legacy)
    db_session.commit()

    payload = TaskQueryService().get_task(db_session, legacy.id)
    assert payload is not None
    assert payload["title"] == "Legacy task without curriculum"
    meta = TaskCurriculumLinkService(db_session).get_task_curriculum_metadata(legacy.id)
    assert meta["has_curriculum_link"] is False


def test_showcase_task_loadable_via_task_query(db_session: Session):
    seed_pascal_loops_showcase(db_session)
    db_session.commit()
    task = find_showcase_task_by_slug(db_session, "counted_loop_tr_python")
    assert task is not None

    payload = TaskQueryService().get_task(db_session, task.id)
    assert payload is not None
    spec = next(s for s in loops_showcase_specs() if s.slug == "counted_loop_tr_python")
    assert payload["title"] == spec.title_suffix
    assert payload["source_language"] == "python"
    assert payload["test_cases"]

