"""Debug code authoring preserves teacher formatting."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from application.tasks.services.assignment_creation_service import create_translation_handler
from application.tasks.use_cases.debug_codes import get_debug_codes_authoring, update_debug_codes
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


def test_debug_codes_preserve_cpp_starter_formatting(db_session: Session):
    formatted_cpp = (
        "#include <iostream>\n"
        "#include <vector>\n"
        "\n"
        "int main() {\n"
        "    int n = int(input());\n"
        "\n"
        "    vector<int> sales = new int[n];\n"
        "\n"
        "    return 0;\n"
        "}\n"
    )
    created = create_translation_handler(
        db_session,
        teacher_id=1,
        title="Debug formatting",
        description="",
        difficulty="hard",
        source_code="using System;",
        source_language="csharp",
        assignment_type="task_translate_full_program",
    )
    task_id = int(created["task_id"])

    update_debug_codes(
        db_session,
        task_id,
        fixed_codes={"csharp": "using System;\nclass Program{\nstatic void Main(){\n  Console.WriteLine(1);\n}}"},
        buggy_codes={"cpp": formatted_cpp},
    )

    payload = get_debug_codes_authoring(db_session, task_id)
    assert payload is not None
    assert payload["buggy_codes"]["cpp"] == formatted_cpp
    assert payload["fixed_codes"]["csharp"] == (
        "using System;\nclass Program{\nstatic void Main(){\n  Console.WriteLine(1);\n}}"
    )

    row = db_session.get(TaskModel, task_id)
    assert row is not None
    examples = row.code_examples or {}
    assert examples["buggy_cpp"] == formatted_cpp
    showcase = examples.get("curriculum_showcase") or {}
    assert "starter_cpp" not in showcase
