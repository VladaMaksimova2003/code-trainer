"""Tests for teacher-managed curriculum chapter metadata."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from application.curriculum.chapters.curriculum_chapter_meta_service import (
    create_chapter,
    list_chapters,
    resolve_chapter_display,
    upsert_chapter,
)
from infrastructure.db.models.base import Base
from infrastructure.db.models.learning.curriculum_chapter_meta import CurriculumChapterMeta
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.user.user import User


@pytest.fixture
def db_session() -> Session:
    load_models()
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[User.__table__, CurriculumChapterMeta.__table__],
    )
    session = sessionmaker(bind=engine)()
    user = User(name="teacher", email="teacher@test.com", password="x", role="teacher")
    session.add(user)
    session.commit()
    try:
        yield session
    finally:
        session.close()


def test_create_and_update_custom_chapter(db_session: Session):
    teacher_id = db_session.query(User).one().id
    row = create_chapter(
        db_session,
        teacher_id=teacher_id,
        language="python",
        title="Моя глава",
        description="Описание главы",
    )
    db_session.commit()

    assert row.chapter_key
    assert row.is_custom is True

    upsert_chapter(
        db_session,
        teacher_id=teacher_id,
        language="python",
        chapter_key=row.chapter_key,
        title="Моя глава (обновлено)",
        description="Новое описание",
    )
    db_session.commit()

    title, description = resolve_chapter_display(
        db_session,
        "python",
        row.chapter_key,
    )
    assert title == "Моя глава (обновлено)"
    assert description == "Новое описание"


def test_override_registry_chapter_title(db_session: Session):
    teacher_id = db_session.query(User).one().id
    upsert_chapter(
        db_session,
        teacher_id=teacher_id,
        language="",
        chapter_key="algo_basics",
        title="Глава 1 — мой заголовок",
        description="Моё описание",
    )
    db_session.commit()

    title, description = resolve_chapter_display(
        db_session,
        "python",
        "algo_basics",
        default_title="Старое название",
    )
    assert title == "Глава 1 — мой заголовок"
    assert description == "Моё описание"
    assert any(item.chapter_key == "algo_basics" for item in list_chapters(db_session))
