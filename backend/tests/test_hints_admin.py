"""Hints: DB override, admin CRUD, core isolation."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from application.analysis.core.educational_validator import EducationalValidator
from application.hints.structure_hint_service import StructureHintService
from infrastructure.db.models.base import Base
from infrastructure.db.models.hints.structure_hint import StructureHintModel
from infrastructure.repositories.hints.structure_hint_repository import (
    StructureHintRepository,
)


@pytest.fixture
def hint_session() -> Session:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[StructureHintModel.__table__],
    )
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


def test_db_overrides_yaml_difficulty(hint_session: Session):
    service = StructureHintService(StructureHintRepository(hint_session))
    yaml_hint = service.get_hint("function", "lambda")
    assert yaml_hint["difficulty"] == 3

    service.upsert_hint(
        structure_type="function",
        subtype="lambda",
        difficulty=1,
        explanation="Custom admin text",
        examples={"python": "lambda x: x"},
        title="Custom Lambda",
    )
    hint_session.commit()

    overridden = service.get_hint("function", "lambda")
    assert overridden["difficulty"] == 1
    assert overridden["explanation"] == "Custom admin text"
    assert overridden["type"] == "function"


def test_upsert_and_delete(hint_session: Session):
    service = StructureHintService(StructureHintRepository(hint_session))
    created = service.upsert_hint(
        structure_type="loop",
        subtype="custom_loop",
        difficulty=2,
        explanation="Test loop hint",
        examples={"python": "while True: pass"},
    )
    hint_session.commit()
    assert created["id"] is not None

    listed = service.list_hints()
    assert any(
        item["type"] == "loop" and item["subtype"] == "custom_loop"
        for item in listed
    )

    assert service.delete_hint(created["id"]) is True
    hint_session.commit()
    assert service.delete_hint(created["id"]) is False


def test_required_with_subtype_does_not_change_pass_fail():
    code = "def f(n):\n    for i in range(n):\n        pass\n"
    without = EducationalValidator().validate(
        code,
        "python",
        [{"type": "function", "min_count": 1}],
    )
    with_subtype = EducationalValidator().validate(
        code,
        "python",
        [{"type": "function", "subtype": "lambda", "min_count": 1}],
    )
    assert without.result == with_subtype.result


def test_core_package_never_imports_hints():
    import ast
    import importlib
    import importlib.util
    import pkgutil

    import infrastructure.analysis.core as core_pkg

    for module_info in pkgutil.walk_packages(
        core_pkg.__path__, core_pkg.__name__ + "."
    ):
        spec = importlib.util.find_spec(module_info.name)
        if not spec or not spec.origin:
            continue
        tree = ast.parse(open(spec.origin, encoding="utf-8").read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "hints" not in alias.name
            if isinstance(node, ast.ImportFrom) and node.module:
                assert "hints" not in node.module
