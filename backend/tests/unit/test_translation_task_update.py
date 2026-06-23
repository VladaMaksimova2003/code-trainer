"""Tests for translation task teacher update use case."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from application.tasks.services.assignment_creation_service import create_translation_handler
from application.tasks.use_cases.translation.task import (
    get_translation_authoring_payload,
    update_translation_task,
)
from infrastructure.db.models.base import Base
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.task.task import Task as TaskModel
from infrastructure.db.models.task.task import TranslationTask
from infrastructure.db.models.task.task_version import TaskVersion


@pytest.fixture
def db_session() -> Session:
    load_models()
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            TaskModel.__table__,
            TranslationTask.__table__,
            TaskVersion.__table__,
        ],
    )
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


def test_update_translation_task_persists_fields(db_session: Session):
    created = create_translation_handler(
        db_session,
        teacher_id=1,
        title="Old title",
        description="Old description",
        difficulty="easy",
        source_code="print('hi')",
        source_language="python",
        assignment_type="task_translate_full_program",
        patterns=["stdout_write"],
        test_cases=[{"name": "T1", "inputs": "", "output": "hi\n"}],
    )
    task_id = int(created["task_id"])

    updated = update_translation_task(
        db_session,
        task_id,
        title="New title",
        description="New description",
        difficulty="medium",
        source_code="print('hello')",
        source_language="python",
        patterns=["stdout_write", "program_entry"],
        test_cases=[{"name": "T1", "inputs": "", "output": "hello\n"}],
    )
    assert updated is not None
    assert updated["title"] == "New title"
    assert updated["source_code"] == "print('hello')"

    payload = get_translation_authoring_payload(db_session, task_id)
    assert payload is not None
    assert payload["difficulty"] == "medium"
    assert payload["patterns"] == ["stdout_write", "program_entry"]
    assert payload["test_cases"][0]["output"] == "hello\n"

    row = db_session.get(TaskModel, task_id)
    assert row is not None
    assert row.title == "New title"
    assert row.version == 2
    assert row.code_examples["python"] == "print('hello')"
    relation = row.translation_task
    assert relation is not None
    assert relation.source_code == "print('hello')"


def test_update_translation_task_preserves_pascal_formatting(db_session: Session):
    pascal_code = (
        "var score: integer;\n"
        "begin\n"
        "  readln(score);\n"
        "  if age >= 18 then\n"
        "  writeln('accepted')\n"
        "  else\n"
        "  writeln('rejected');\n"
        "end."
    )
    created = create_translation_handler(
        db_session,
        teacher_id=1,
        title="Pascal formatting",
        description="",
        difficulty="hard",
        source_code=pascal_code,
        source_language="pascal",
        assignment_type="task_translate_full_program",
    )
    task_id = int(created["task_id"])

    payload = get_translation_authoring_payload(db_session, task_id)
    assert payload is not None
    assert payload["source_code"] == pascal_code
    assert payload["language_codes"]["pascal"] == pascal_code

    row = db_session.get(TaskModel, task_id)
    assert row is not None
    assert row.translation_task is not None
    assert row.translation_task.source_code == pascal_code
    assert row.code_examples["pascal"] == pascal_code


def test_update_translation_task_preserves_other_language_codes(db_session: Session):
    created = create_translation_handler(
        db_session,
        teacher_id=1,
        title="Multi",
        description="",
        difficulty="easy",
        source_code="print(1)",
        source_language="python",
        assignment_type="task_translate_full_program",
    )
    task_id = int(created["task_id"])
    row = db_session.get(TaskModel, task_id)
    assert row is not None
    examples = dict(row.code_examples or {})
    examples["cpp"] = "#include <iostream>\nint main() { return 0; }"
    examples["pascal"] = "begin\n  writeln(1);\nend."
    row.code_examples = examples
    db_session.commit()

    update_translation_task(
        db_session,
        task_id,
        title="Multi",
        description="",
        difficulty="easy",
        source_code="print(2)",
        source_language="python",
        language_codes={
            "python": "print(2)",
            "cpp": examples["cpp"],
            "pascal": examples["pascal"],
        },
    )

    row = db_session.get(TaskModel, task_id)
    assert row is not None
    saved = row.code_examples or {}
    assert saved["python"] == "print(2)"
    assert "iostream" in str(saved.get("cpp") or "")
    assert "writeln" in str(saved.get("pascal") or "")

    payload = get_translation_authoring_payload(db_session, task_id)
    assert payload is not None
    assert payload["language_codes"]["cpp"] == saved["cpp"]
    assert payload["language_codes"]["pascal"] == saved["pascal"]
