from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from application.learning.services.assignment_set_progress import (
    active_task_ids,
    assignment_set_progress,
)
from infrastructure.db.models.base import Base
from infrastructure.db.models.learning.submission import Submission
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.task.task import Task as TaskModel
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
            Submission.__table__,
        ],
    )
    session = sessionmaker(bind=engine)()
    session.add(User(name="Student", email="student@test.local", password="hash", role="student"))
    session.commit()
    try:
        yield session
    finally:
        session.close()


def _task(title: str, *, deleted: bool = False) -> TaskModel:
    return TaskModel(
        title=title,
        description="",
        task_type="task_translate_snippet",
        difficulty="easy",
        test_cases=[],
        code_examples={},
        flow_spec={},
        is_delete=deleted,
    )


def test_assignment_set_progress_ignores_deleted_tasks(db_session: Session):
    user_id = db_session.query(User).first().id
    active = _task("Active")
    deleted = _task("Deleted", deleted=True)
    db_session.add_all([active, deleted])
    db_session.commit()

    total, solved = assignment_set_progress(
        db_session,
        user_id=user_id,
        task_ids=[active.id, deleted.id],
    )
    assert total == 1
    assert solved == 0


def test_assignment_set_progress_counts_solved(db_session: Session):
    user_id = db_session.query(User).first().id
    task = _task("Done")
    db_session.add(task)
    db_session.flush()
    db_session.add(
        Submission(
            user_id=user_id,
            task_id=task.id,
            language="python",
            code="print(1)",
            status="done",
            success=True,
        )
    )
    db_session.commit()

    total, solved = assignment_set_progress(
        db_session,
        user_id=user_id,
        task_ids=[task.id],
    )
    assert total == 1
    assert solved == 1


def test_active_task_ids_filters_deleted(db_session: Session):
    active = _task("Active")
    deleted = _task("Deleted", deleted=True)
    db_session.add_all([active, deleted])
    db_session.commit()

    ids = active_task_ids(db_session, [active.id, deleted.id])
    assert ids == [active.id]
