"""StructureHintResolver — DB overrides YAML, no field merge."""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from application.hints.structure_hint_resolver import StructureHintResolver
from infrastructure.db.models.base import Base
from infrastructure.db.models.hints.structure_hint import StructureHintModel
from infrastructure.repositories.hints.structure_hint_repository import (
    StructureHintRepository,
)


def test_db_replaces_yaml_entirely():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine, tables=[StructureHintModel.__table__])
    session = sessionmaker(bind=engine)()
    repo = StructureHintRepository(session)
    repo.upsert(
        structure_type="function",
        subtype="lambda",
        difficulty=1,
        explanation="Only from DB",
        examples={"python": "custom"},
        title="DB Lambda",
    )
    session.commit()

    resolver = StructureHintResolver(repo)
    record = resolver.resolve("function", "lambda")
    assert record.source == "db"
    assert record.difficulty == 1
    assert record.explanation == "Only from DB"
    assert record.to_api_dict()["type"] == "function"
    assert record.to_api_dict()["subtype"] == "lambda"


def test_defaults_when_missing():
    resolver = StructureHintResolver(None)
    record = resolver.resolve("unknown_structure", None)
    assert record.subtype == "default"
    assert record.difficulty == 1
