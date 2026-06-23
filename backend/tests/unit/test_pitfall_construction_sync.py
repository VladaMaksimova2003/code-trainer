"""Tests for pitfall catalog export into Construction library (stage 2)."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from application.curriculum.display.pitfall_catalog import PITFALLS, list_pitfall_ids
from application.curriculum.display.pitfall_construction_sync import (
    MPLT_CATEGORY_NAME,
    build_construction_description,
    list_mplt_constructions,
    parse_export_pitfall_id,
    sync_pitfall_constructions,
)
from infrastructure.db.models.base import Base
from infrastructure.db.models.task.construction import CategoryConstruction, Construction
from infrastructure.db.models.task.registry import load_models


@pytest.fixture
def db_session() -> Session:
    load_models()
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            CategoryConstruction.__table__,
            Construction.__table__,
        ],
    )
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


def test_build_construction_description_contains_export_marker():
    spec = PITFALLS["integer_division"]
    text = build_construction_description(spec)
    assert "pitfall_id=integer_division" in text
    assert "transfer_type=FCC" in text
    assert parse_export_pitfall_id(text) == "integer_division"


def test_sync_creates_one_row_per_pitfall(db_session: Session):
    report = sync_pitfall_constructions(db_session, dry_run=False)
    db_session.commit()

    assert len(PITFALLS) == len(list_pitfall_ids())
    assert report.totals["created"] == len(PITFALLS)
    assert report.category_id is not None

    category = db_session.scalar(
        select(CategoryConstruction).where(CategoryConstruction.name == MPLT_CATEGORY_NAME)
    )
    assert category is not None
    rows = db_session.scalars(
        select(Construction).where(Construction.category_id == category.id)
    ).all()
    assert len(rows) == len(PITFALLS)


def test_sync_is_idempotent(db_session: Session):
    sync_pitfall_constructions(db_session, dry_run=False)
    db_session.commit()
    second = sync_pitfall_constructions(db_session, dry_run=False)
    db_session.commit()

    assert second.totals["created"] == 0
    assert second.totals["updated"] == 0
    assert second.totals["skipped"] == len(PITFALLS)


def test_sync_updates_changed_catalog_text(db_session: Session):
    sync_pitfall_constructions(db_session, dry_run=False)
    db_session.commit()
    pitfall_id = "integer_division"
    row = db_session.scalar(
        select(Construction).where(Construction.name == f"MPLT:{pitfall_id}")
    )
    assert row is not None
    row.description = "stale"
    db_session.commit()

    second = sync_pitfall_constructions(db_session, dry_run=False)
    db_session.commit()
    assert pitfall_id in second.updated

    refreshed = db_session.scalar(select(Construction).where(Construction.id == row.id))
    assert refreshed is not None
    assert parse_export_pitfall_id(refreshed.description or "") == pitfall_id


def test_list_mplt_constructions_after_seed(db_session: Session):
    sync_pitfall_constructions(db_session, dry_run=False)
    db_session.commit()
    items = list_mplt_constructions(db_session)
    assert len(items) == len(PITFALLS)
    assert all(item.get("pitfall_id") for item in items)
    assert all(item.get("transfer_type") for item in items)
