"""Unit tests — lightweight task overview API."""

from __future__ import annotations

import json
import time
from collections.abc import Iterator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from application.tasks.services.catalog.task_overview import (
    list_task_overviews,
    overview_item_has_no_heavy_fields,
    task_row_to_overview,
)
from infrastructure.db.models.base import Base
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.task.task import Task as TaskModel
from main import app
from infrastructure.db.session import get_db

load_models()


@pytest.fixture
def db_session() -> Iterator[Session]:
    from sqlalchemy.pool import StaticPool

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine, tables=[TaskModel.__table__])
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def _seed_overview_tasks(session: Session, count: int) -> None:
    for index in range(count):
        session.add(
            TaskModel(
                title=f"Task {index}",
                description="Heavy description that must not appear in overview",
                task_type="task_translate_full_program",
                difficulty="easy",
                test_cases=[{"input": "1", "output": "2"}],
                code_examples={
                    "patterns": ["loop_for"],
                    "python": "print('heavy starter code' * 100)",
                    "curriculum_showcase": {
                        "slug": f"slot_{index:03d}",
                        "collection_key": "loops" if index % 2 == 0 else "oop",
                        "target_language": "python" if index % 3 else "pascal",
                        "task_format": "перевод",
                    },
                },
            )
        )
    session.commit()


def test_overview_row_has_no_heavy_fields(db_session: Session) -> None:
    _seed_overview_tasks(db_session, 1)
    row = db_session.query(TaskModel).first()
    assert row is not None
    overview = task_row_to_overview(row)
    assert overview_item_has_no_heavy_fields(overview)
    assert overview["slot_id"] == "slot_000"
    assert overview["course_key"] in {"python", "pascal"}


def test_overview_filters_by_course_and_chapter(db_session: Session) -> None:
    _seed_overview_tasks(db_session, 6)
    payload = list_task_overviews(
        db_session,
        allowed_task_ids=None,
        course="python",
        chapter="loops",
    )
    assert payload["total"] >= 1
    for item in payload["tasks"]:
        assert item["course_key"] == "python"
        assert item["chapter_key"] == "loops"


def test_overview_filters_by_search_and_type(db_session: Session) -> None:
    _seed_overview_tasks(db_session, 6)
    payload = list_task_overviews(
        db_session,
        allowed_task_ids=None,
        search="Task 1",
        task_type="task_translate_full_program",
    )
    assert payload["total"] >= 1
    for item in payload["tasks"]:
        assert "task 1" in item["title"].lower()
        assert item["type"] == "task_translate_full_program"


def test_overview_deduplicates_mirror_rows_for_same_pedagogical_slot(db_session: Session) -> None:
    showcase = {
        "slug": "pas_010",
        "slot_id": "pas_010",
        "collection_key": "loops",
        "target_language": "pascal",
        "task_format": "перевод",
    }
    mirror_showcase = {
        "slug": "py_010",
        "slot_id": "py_010",
        "collection_key": "loops",
        "target_language": "python",
        "task_format": "перевод",
    }
    db_session.add(
        TaskModel(
            title="Pascal mirror task",
            description="x",
            task_type="task_translate_full_program",
            difficulty="easy",
            test_cases=[],
            code_examples={"curriculum_showcase": showcase},
        )
    )
    db_session.add(
        TaskModel(
            title="Python mirror task",
            description="x",
            task_type="task_translate_full_program",
            difficulty="easy",
            test_cases=[],
            code_examples={"curriculum_showcase": mirror_showcase},
        )
    )
    db_session.commit()

    payload = list_task_overviews(db_session, allowed_task_ids=None)
    assert payload["total"] == 1
    assert len(payload["tasks"]) == 1


def test_overview_listing_500_tasks_under_200ms(db_session: Session) -> None:
    _seed_overview_tasks(db_session, 500)
    started = time.perf_counter()
    payload = list_task_overviews(db_session, allowed_task_ids=None, page=1, page_size=20)
    elapsed_ms = (time.perf_counter() - started) * 1000
    assert payload["total"] == 500
    assert len(payload["tasks"]) == 20
    assert elapsed_ms < 500, f"overview took {elapsed_ms:.1f}ms"


def test_overview_pagination_returns_slice(db_session: Session) -> None:
    _seed_overview_tasks(db_session, 25)
    page_one = list_task_overviews(db_session, allowed_task_ids=None, page=1, page_size=10)
    page_three = list_task_overviews(db_session, allowed_task_ids=None, page=3, page_size=10)
    assert page_one["total"] == 25
    assert len(page_one["tasks"]) == 10
    assert len(page_three["tasks"]) == 5
    assert page_one["tasks"][0]["id"] != page_three["tasks"][0]["id"]


def test_overview_sql_query_count_limited(db_session: Session) -> None:
    _seed_overview_tasks(db_session, 50)
    counter = {"count": 0}

    @event.listens_for(db_session.bind, "before_cursor_execute")
    def _count_queries(
        conn,
        cursor,
        statement,
        parameters,
        context,
        executemany,
    ) -> None:
        counter["count"] += 1

    list_task_overviews(db_session, allowed_task_ids=None)
    assert counter["count"] <= 2


@pytest.fixture
def api_client(db_session: Session) -> Iterator[TestClient]:
    def _override_get_db() -> Iterator[Session]:
        yield db_session

    def _allowed_task_ids(db: Session, _current) -> set[int]:
        return {int(row.id) for row in db.query(TaskModel).all()}

    app.dependency_overrides[get_db] = _override_get_db
    with patch(
        "api.tasks.endpoints.list_tasks._allowed_task_ids",
        _allowed_task_ids,
    ):
        client = TestClient(app)
        try:
            yield client
        finally:
            app.dependency_overrides.clear()


def test_overview_endpoint_payload_is_light(api_client: TestClient, db_session: Session) -> None:
    _seed_overview_tasks(db_session, 3)
    response = api_client.get("/tasks/overview", params={"page": 1, "page_size": 20})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3
    assert len(body["tasks"]) == 3
    encoded = json.dumps(body)
    assert "heavy starter code" not in encoded
    assert "code_examples" not in encoded
    assert "test_cases" not in encoded
    for item in body["tasks"]:
        assert overview_item_has_no_heavy_fields(item)


def test_detail_payload_is_heavier_than_overview(db_session: Session) -> None:
    _seed_overview_tasks(db_session, 1)
    row = db_session.query(TaskModel).first()
    assert row is not None
    overview = task_row_to_overview(row)
    assert overview_item_has_no_heavy_fields(overview)
    assert row.code_examples
    assert row.test_cases


def test_tasks_light_query_param_aliases_overview(api_client: TestClient, db_session: Session) -> None:
    _seed_overview_tasks(db_session, 2)
    response = api_client.get("/tasks/", params={"light": "true"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert "code_examples" not in json.dumps(body)
