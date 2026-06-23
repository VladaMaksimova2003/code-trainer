"""Unit tests  -  student curriculum progress MVP."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from application.curriculum.pascal.legacy.loops.loops_showcase_seeder import seed_pascal_loops_showcase
from application.curriculum.pascal.legacy.loops.loops_showcase_student import build_pascal_loops_showcase_student_view
from application.curriculum.progress.submission_curriculum_progress import record_curriculum_progress_safe
from application.curriculum.progress.student_curriculum_progress_service import (
    PROGRESS_STATUS_FAILED,
    PROGRESS_STATUS_NOT_STARTED,
    PROGRESS_STATUS_PASSED,
    StudentCurriculumProgressService,
)
from infrastructure.db.models.base import Base
from infrastructure.db.models.learning.student_curriculum_progress import (
    StudentCurriculumProgressModel,
)
from infrastructure.db.models.learning.submission import Submission
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
            Submission.__table__,
            StudentCurriculumProgressModel.__table__,
        ],
    )
    session = sessionmaker(bind=engine)()
    user = User(name="Student", email="student@test.local", password="hash", role="student")
    session.add(user)
    session.commit()
    try:
        yield session
    finally:
        session.close()


def _create_submission(db: Session, user_id: int, task_id: int, *, success: bool) -> Submission:
    sub = Submission(
        user_id=user_id,
        task_id=task_id,
        language="pascal",
        code="program test; begin end.",
        status="done",
        success=success,
    )
    db.add(sub)
    db.flush()
    return sub


def test_legacy_task_without_curriculum_link_creates_no_progress(db_session: Session):
    user_id = db_session.query(User).first().id
    legacy = TaskModel(
        title="Legacy",
        description="no link",
        task_type="task_translate_snippet",
        difficulty="easy",
        test_cases=[],
        code_examples={},
        flow_spec={},
    )
    db_session.add(legacy)
    db_session.commit()

    sub = _create_submission(db_session, user_id, legacy.id, success=True)
    db_session.commit()

    svc = StudentCurriculumProgressService(db_session)
    svc.record_submission_result(user_id, sub.id, legacy.id, passed=True)
    db_session.commit()

    rows = db_session.query(StudentCurriculumProgressModel).all()
    assert rows == []


def test_failed_submission_records_attempt_without_pass(db_session: Session):
    seed_pascal_loops_showcase(db_session)
    db_session.commit()

    user_id = db_session.query(User).first().id
    task_id = db_session.query(TaskModel).first().id
    sub = _create_submission(db_session, user_id, task_id, success=False)
    db_session.commit()

    svc = StudentCurriculumProgressService(db_session)
    svc.record_submission_result(user_id, sub.id, task_id, passed=False)
    db_session.commit()

    row = db_session.query(StudentCurriculumProgressModel).one()
    assert row.attempts_count == 1
    assert row.passed_count == 0
    assert row.last_status == "failed"
    assert row.first_passed_at is None

    progress = svc.get_progress_for_task(user_id, task_id)
    assert progress["progress_status"] == PROGRESS_STATUS_FAILED


def test_passed_submission_marks_task_as_passed(db_session: Session):
    seed_pascal_loops_showcase(db_session)
    db_session.commit()

    user_id = db_session.query(User).first().id
    payload = build_pascal_loops_showcase_student_view(db_session)
    task_id = payload["technical_concepts"][0]["tasks"][0]["task_id"]
    sub = _create_submission(db_session, user_id, task_id, success=True)
    db_session.commit()

    svc = StudentCurriculumProgressService(db_session)
    svc.record_submission_result(user_id, sub.id, task_id, passed=True)
    db_session.commit()

    row = db_session.query(StudentCurriculumProgressModel).one()
    assert row.passed_count == 1
    assert row.last_status == "passed"
    assert row.first_passed_at is not None
    assert row.technical_concept_id == "counted_loop"
    assert row.action == "translate"

    progress = svc.get_progress_for_task(user_id, task_id)
    assert progress["progress_status"] == PROGRESS_STATUS_PASSED


def test_repeat_passed_does_not_duplicate_progress(db_session: Session):
    seed_pascal_loops_showcase(db_session)
    db_session.commit()

    user_id = db_session.query(User).first().id
    task_id = db_session.query(TaskModel).first().id
    svc = StudentCurriculumProgressService(db_session)

    sub1 = _create_submission(db_session, user_id, task_id, success=True)
    db_session.commit()
    svc.record_submission_result(user_id, sub1.id, task_id, passed=True)
    db_session.commit()

    row = db_session.query(StudentCurriculumProgressModel).one()
    first_passed_at = row.first_passed_at

    sub2 = _create_submission(db_session, user_id, task_id, success=True)
    db_session.commit()
    svc.record_submission_result(user_id, sub2.id, task_id, passed=True)
    db_session.commit()

    rows = db_session.query(StudentCurriculumProgressModel).all()
    assert len(rows) == 1
    assert rows[0].passed_count == 1
    assert rows[0].attempts_count == 2
    assert rows[0].first_passed_at == first_passed_at


def test_student_endpoint_returns_progress_when_user_authenticated(db_session: Session):
    seed_pascal_loops_showcase(db_session)
    db_session.commit()

    user_id = db_session.query(User).first().id
    payload = build_pascal_loops_showcase_student_view(db_session)
    task_id = payload["technical_concepts"][0]["tasks"][0]["task_id"]
    sub = _create_submission(db_session, user_id, task_id, success=True)
    db_session.commit()

    StudentCurriculumProgressService(db_session).record_submission_result(
        user_id, sub.id, task_id, passed=True
    )
    db_session.commit()

    anonymous = build_pascal_loops_showcase_student_view(db_session)
    assert "progress" not in anonymous
    assert anonymous["technical_concepts"][0]["tasks"][0]["progress_status"] == PROGRESS_STATUS_NOT_STARTED

    with_progress = build_pascal_loops_showcase_student_view(db_session, user_id=user_id)
    assert with_progress["progress"]["passed_tasks"] == 1
    assert with_progress["progress"]["total_tasks"] == 7
    assert with_progress["progress"]["progress_percent"] == round(100 / 7, 1)

    first_task = with_progress["technical_concepts"][0]["tasks"][0]
    assert first_task["progress_status"] == PROGRESS_STATUS_PASSED
    assert with_progress["technical_concepts"][0]["progress"]["passed_tasks"] == 1

    failed_task_id = payload["technical_concepts"][0]["tasks"][1]["task_id"]
    sub_fail = _create_submission(db_session, user_id, failed_task_id, success=False)
    db_session.commit()
    StudentCurriculumProgressService(db_session).record_submission_result(
        user_id, sub_fail.id, failed_task_id, passed=False
    )
    db_session.commit()

    mixed = build_pascal_loops_showcase_student_view(db_session, user_id=user_id)
    failed_card = mixed["technical_concepts"][0]["tasks"][1]
    assert failed_card["progress_status"] == PROGRESS_STATUS_FAILED


def test_record_curriculum_progress_safe_loads_models(db_session: Session, monkeypatch):
    seed_pascal_loops_showcase(db_session)
    db_session.commit()

    user_id = db_session.query(User).first().id
    task_id = db_session.query(TaskModel).first().id
    sub = Submission(
        user_id=user_id,
        task_id=task_id,
        language="pascal",
        code="begin end.",
        status="done",
        success=True,
    )
    db_session.add(sub)
    db_session.commit()

    monkeypatch.setattr(
        "infrastructure.db.session.SessionLocal",
        sessionmaker(bind=db_session.get_bind()),
    )

    record_curriculum_progress_safe(
        user_id=user_id,
        submission_id=sub.id,
        task_id=task_id,
        passed=True,
    )

    row = db_session.query(StudentCurriculumProgressModel).one()
    assert row.passed_count == 1


def test_passed_submission_is_tracked_per_language(db_session: Session):
    user_id = db_session.query(User).first().id
    task = TaskModel(
        title="Unified loop",
        description="multi-track",
        task_type="task_translate_snippet",
        difficulty="easy",
        test_cases=[],
        code_examples={},
        flow_spec={},
    )
    db_session.add(task)
    db_session.flush()

    db_session.add(
        TaskCurriculumLinkModel(
            task_id=task.id,
            language="pascal",
            learning_concept_id="loops",
            technical_concept_id="counted_loop",
            exercise_pattern_id="tr_python_to_pascal_code",
            action="translate",
            is_primary=True,
        )
    )
    db_session.add(
        TaskCurriculumLinkModel(
            task_id=task.id,
            language="python",
            learning_concept_id="loops",
            technical_concept_id="counted_loop",
            exercise_pattern_id="tr_pascal_to_python_code",
            action="translate",
            is_primary=False,
        )
    )
    db_session.commit()

    svc = StudentCurriculumProgressService(db_session)
    sub_cpp = Submission(
        user_id=user_id,
        task_id=task.id,
        language="cpp",
        code="int main() {}",
        status="done",
        success=True,
    )
    db_session.add(sub_cpp)
    db_session.flush()
    svc.record_submission_result(user_id, sub_cpp.id, task.id, passed=True)
    db_session.commit()
    assert db_session.query(StudentCurriculumProgressModel).count() == 0

    sub_py = Submission(
        user_id=user_id,
        task_id=task.id,
        language="python",
        code="print('hi')",
        status="done",
        success=True,
    )
    db_session.add(sub_py)
    db_session.flush()
    svc.record_submission_result(user_id, sub_py.id, task.id, passed=True)
    db_session.commit()

    rows = db_session.query(StudentCurriculumProgressModel).all()
    assert len(rows) == 1
    assert rows[0].language == "python"
    assert rows[0].passed_count == 1

    py_progress = svc.get_progress_for_learning_concept(
        user_id,
        "python",
        "loops",
        task_ids=[task.id],
    )
    pascal_progress = svc.get_progress_for_learning_concept(
        user_id,
        "pascal",
        "loops",
        task_ids=[task.id],
    )
    assert py_progress["passed_tasks"] == 1
    assert pascal_progress["passed_tasks"] == 0
    assert (
        py_progress["by_task_id"][task.id]["progress_status"] == PROGRESS_STATUS_PASSED
    )
    assert (
        pascal_progress["by_task_id"][task.id]["progress_status"]
        == PROGRESS_STATUS_NOT_STARTED
    )

    sub_pascal = Submission(
        user_id=user_id,
        task_id=task.id,
        language="pascal",
        code="begin end.",
        status="done",
        success=True,
    )
    db_session.add(sub_pascal)
    db_session.flush()
    svc.record_submission_result(user_id, sub_pascal.id, task.id, passed=True)
    db_session.commit()

    assert db_session.query(StudentCurriculumProgressModel).count() == 2
    pascal_progress = svc.get_progress_for_learning_concept(
        user_id,
        "pascal",
        "loops",
        task_ids=[task.id],
    )
    assert pascal_progress["passed_tasks"] == 1


def test_learning_concept_progress_falls_back_to_successful_submissions(db_session: Session):
    user_id = db_session.query(User).first().id
    task = TaskModel(
        title="Python only",
        description="no curriculum row yet",
        task_type="task_translate_snippet",
        difficulty="easy",
        test_cases=[],
        code_examples={},
        flow_spec={},
    )
    db_session.add(task)
    db_session.flush()
    db_session.add(
        TaskCurriculumLinkModel(
            task_id=task.id,
            language="python",
            learning_concept_id="loops",
            technical_concept_id="counted_loop",
            exercise_pattern_id="tr_pascal_to_python_code",
            action="translate",
            is_primary=True,
        )
    )
    sub = Submission(
        user_id=user_id,
        task_id=task.id,
        language="python",
        code="print('ok')",
        status="done",
        success=True,
    )
    db_session.add(sub)
    db_session.commit()

    svc = StudentCurriculumProgressService(db_session)
    progress = svc.get_progress_for_learning_concept(
        user_id,
        "python",
        "loops",
        task_ids=[task.id],
    )
    assert progress["passed_tasks"] == 1
    assert progress["by_task_id"][task.id]["progress_status"] == PROGRESS_STATUS_PASSED

