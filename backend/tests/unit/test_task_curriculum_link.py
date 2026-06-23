"""Unit tests — task ↔ curriculum v2 links (stage 2)."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from application.curriculum.task_curriculum_link_service import (
    TaskCurriculumLinkService,
    validate_task_curriculum_link_metadata,
)
from domain.learning.curriculum.task_link_exceptions import TaskCurriculumLinkValidationError
from infrastructure.db.models.base import Base
from infrastructure.db.models.task.task import Task
from infrastructure.db.models.task.task_curriculum_link import TaskCurriculumLinkModel
from shared.enums import Difficulty, TaskType, TaskVisibility
from shared.exceptions import TaskNotFoundError


from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.user.user import User


@pytest.fixture
def db_session() -> Session:
    load_models()
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[User.__table__, Task.__table__, TaskCurriculumLinkModel.__table__],
    )
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


def _create_task(session: Session, *, task_id: int = 1) -> Task:
    task = Task(
        id=task_id,
        title="Loop translate",
        description="test",
        task_type=TaskType.TRANSLATION.value,
        difficulty=Difficulty.EASY.value,
        visibility=TaskVisibility.PUBLIC,
        test_cases=[],
        code_examples={},
        flow_spec={},
    )
    session.add(task)
    session.flush()
    return task


def test_link_counted_loop_python_translate(db_session: Session):
    _create_task(db_session)
    svc = TaskCurriculumLinkService(db_session)
    link = svc.link_task_to_curriculum(
        1,
        "pascal",
        "counted_loop",
        "tr_python_to_pascal_code",
        is_primary=True,
    )
    db_session.commit()

    assert link.learning_concept_id == "loops"
    assert link.technical_concept_id == "counted_loop"
    assert link.exercise_pattern_id == "tr_python_to_pascal_code"
    assert link.action == "translate"
    assert link.is_primary is True

    links = svc.get_task_curriculum_links(1)
    assert len(links) == 1


def test_cannot_link_loop_control_to_assemble_pattern(db_session: Session):
    _create_task(db_session)
    svc = TaskCurriculumLinkService(db_session)
    with pytest.raises(TaskCurriculumLinkValidationError, match="disabled"):
        svc.link_task_to_curriculum(
            1,
            "pascal",
            "loop_control",
            "asm_flowchart_to_blocks",
        )


def test_cannot_link_unknown_pattern(db_session: Session):
    with pytest.raises(TaskCurriculumLinkValidationError, match="Unknown exercise pattern"):
        validate_task_curriculum_link_metadata(
            "pascal",
            "counted_loop",
            "tr_does_not_exist",
        )


def test_action_is_taken_from_pattern(db_session: Session):
    meta = validate_task_curriculum_link_metadata(
        "pascal",
        "counted_loop",
        "tr_cpp_to_pascal_code",
    )
    assert meta["action"] == "translate"
    assert meta["learning_concept_id"] == "loops"


def test_task_without_link_returns_empty_metadata(db_session: Session):
    _create_task(db_session)
    svc = TaskCurriculumLinkService(db_session)
    meta = svc.get_task_curriculum_metadata(1)
    assert meta["has_curriculum_link"] is False
    assert meta["links"] == []
    assert meta["primary_link"] is None


def test_task_without_link_does_not_affect_task_existence(db_session: Session):
    _create_task(db_session)
    svc = TaskCurriculumLinkService(db_session)
    meta = svc.get_task_curriculum_metadata(1)
    assert meta["task_id"] == 1
    links = svc.get_task_curriculum_links(1)
    assert links == []


def test_missing_task_raises_not_found(db_session: Session):
    svc = TaskCurriculumLinkService(db_session)
    with pytest.raises(TaskNotFoundError):
        svc.get_task_curriculum_links(999)


def test_duplicate_pattern_link_rejected(db_session: Session):
    _create_task(db_session)
    svc = TaskCurriculumLinkService(db_session)
    svc.link_task_to_curriculum(
        1,
        "pascal",
        "counted_loop",
        "tr_python_to_pascal_code",
    )
    db_session.commit()
    with pytest.raises(TaskCurriculumLinkValidationError, match="already linked"):
        svc.link_task_to_curriculum(
            1,
            "pascal",
            "counted_loop",
            "tr_python_to_pascal_code",
        )


def test_delete_link(db_session: Session):
    _create_task(db_session)
    svc = TaskCurriculumLinkService(db_session)
    link = svc.link_task_to_curriculum(
        1,
        "pascal",
        "counted_loop",
        "tr_python_to_pascal_code",
    )
    db_session.commit()
    svc.delete_link(1, link.id)
    db_session.commit()
    assert svc.get_task_curriculum_links(1) == []
