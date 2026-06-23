"""Tests for C++ Course v1.1 MVP-1 catalog and Universal Core integration."""

from __future__ import annotations

import re
from collections.abc import Iterator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from application.curriculum.cpp.catalog.cpp_curriculum_v3_catalog import (
    V311_TOTAL_TASKS,
    all_v311_task_records,
    catalog_summary,
    validate_v311_catalog,
)
from application.curriculum.cpp.catalog.cpp_v311_expected_concepts import expected_concept_ids_for_row
from application.curriculum.cpp.showcase.cpp_v311_registry import (
    CPP_V311_SHOWCASE_COLLECTIONS,
    V311_CHAPTER_ORDER,
    V311_COLLECTION_TARGETS,
)
from application.curriculum.mirror.curriculum_slot_mirror_cpp import (
    CPP_ONLY_SLOTS,
    chapters_for_stage,
    is_cpp_only_slot,
)
from application.curriculum.mirror.pedagogical_task_model import merge_showcase_pair, normalize_unified_showcase
from application.curriculum.mirror.pedagogical_task_store import (
    apply_learning_language_to_payload,
    attach_unified_showcase_meta,
    merge_language_track,
)
from application.curriculum.mirror.universal_core_validation import validate_no_duplicate_pedagogical_slot_ids
from application.tasks.services.catalog.task_overview import list_task_overviews, task_row_to_overview
from infrastructure.db.models.base import Base
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.task.task import Task as TaskModel
from infrastructure.db.session import get_db
from main import app

load_models()

LANG_PATTERN = re.compile(r"pascal|python|java|c#|csharp", re.I)


def _showcase(*, slug: str, language: str, chapter: str, ped_id: str | None = None) -> dict:
    base = {
        "slug": slug,
        "slot_id": slug,
        "target_language": language,
        "collection_key": chapter,
        "task_format": "перевод_фрагмента",
        "primary_action": "translate",
        "exercise_pattern_id": f"tr_{slug}",
        "educational_goal": "Language-neutral goal",
    }
    if ped_id:
        base["pedagogical_slot_id"] = ped_id
    return base


def _cpp_track(slug: str, chapter: str) -> dict:
    return {
        "slug": slug,
        "slot_id": slug,
        "collection_key": chapter,
        "target_language": "cpp",
        "language": "cpp",
        "primary_action": "translate",
        "exercise_pattern_id": "tr_python_to_pascal_code",
        "educational_goal": f"C++ goal for {slug}",
        "cpp_features": "iostream",
    }


@pytest.fixture
def db_session() -> Iterator[Session]:
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


def _add_task(session: Session, *, task_id: int, title: str, showcase: dict) -> TaskModel:
    row = TaskModel(
        id=task_id,
        title=title,
        description="detail",
        task_type="task_translate_fragment",
        difficulty="easy",
        is_delete=False,
        code_examples={"curriculum_showcase": showcase, "patterns": ["loop_for"]},
    )
    session.add(row)
    session.commit()
    return row


def test_cpp_stage1_catalog_count():
    records = all_v311_task_records()
    assert len(records) == V311_TOTAL_TASKS == 237
    assert len(V311_CHAPTER_ORDER) == 26
    assert sum(V311_COLLECTION_TARGETS.values()) == V311_TOTAL_TASKS
    errors = validate_v311_catalog()
    assert errors == [], errors


def test_cpp_chapters_for_stage_all():
    assert chapters_for_stage("all") == V311_CHAPTER_ORDER
    assert len(chapters_for_stage("all")) == 26


def test_cpp_v1full_chapter_targets():
    summary = catalog_summary()
    assert summary["total_tasks"] == 237
    assert summary["mirror_attach_tasks"] == 118
    assert summary["cpp_only_tasks"] == 119
    assert V311_COLLECTION_TARGETS["cpp_oop"] == 12
    assert V311_COLLECTION_TARGETS["cpp_pointers"] == 16
    assert V311_COLLECTION_TARGETS["cpp_move"] == 7
    assert V311_COLLECTION_TARGETS["cpp_exceptions"] == 8
    assert V311_COLLECTION_TARGETS["cpp_capstones"] == 8


def test_cpp_v12_exceptions_and_capstones():
    keys = {c.chapter_key for c in CPP_V311_SHOWCASE_COLLECTIONS}
    assert "cpp_exceptions" in keys
    assert "cpp_capstones" in keys
    capstones = [r for r in all_v311_task_records() if r.chapter_key == "cpp_capstones"]
    assert len(capstones) == 8
    assert all(r.slot_id.startswith("cpcap_") for r in capstones)
    assert all(is_cpp_only_slot(r.slot_id) for r in capstones)
    mirrors = [r for r in all_v311_task_records() if r.chapter_key == "cpp_exceptions"]
    assert len(mirrors) == 8
    assert all(r.pascal_mirror.startswith("exc_") for r in mirrors)


def test_cpp_v11_group_c_chapters():
    keys = {c.chapter_key for c in CPP_V311_SHOWCASE_COLLECTIONS}
    for chapter in (
        "cpp_preprocessor",
        "cpp_templates",
        "cpp_enums",
        "cpp_stl_associative",
        "cpp_stl_algorithms",
        "cpp_move",
    ):
        assert chapter in keys


def test_cpp_no_analyze_or_matching():
    for rec in all_v311_task_records():
        assert rec.primary_action != "analyze"
        assert rec.task_format != "сопоставление"


def test_cpp_expected_concepts_present():
    for rec in all_v311_task_records():
        concepts = expected_concept_ids_for_row(rec.slot_id, rec.chapter_key, _features=rec.cpp_features)
        assert concepts, f"{rec.slot_id}: missing expected concepts"


def test_cpp_collections_registered():
    assert len(CPP_V311_SHOWCASE_COLLECTIONS) == 26
    keys = {c.chapter_key for c in CPP_V311_SHOWCASE_COLLECTIONS}
    assert "cpp_oop" in keys
    assert "cpp_diagnostics" in keys
    assert "cpp_move" in keys
    assert "cpp_capstones" in keys


def test_cpp_catalog_summary():
    summary = catalog_summary()
    assert summary["total_tasks"] == 237
    assert summary["chapters"] == 26


def test_cpp_tracks_attached_to_universal_core(db_session: Session):
    merged = merge_showcase_pair(
        _showcase(slug="psk_01", language="pascal", chapter="program_skeleton", ped_id="psk_01"),
        _showcase(slug="pyk_01", language="python", chapter="program_entry"),
        pedagogical_slot_id="psk_01",
    )
    row = _add_task(db_session, task_id=1, title="[Pascal v3.1.1: Unified]", showcase=merged)
    attach_unified_showcase_meta(row, _cpp_track("cpk_01", "cpp_entry"), "cpp")
    db_session.commit()

    showcase = dict((row.code_examples or {}).get("curriculum_showcase") or {})
    showcase = normalize_unified_showcase(showcase)
    assert showcase["pedagogical_slot_id"] == "psk_01"
    assert showcase["language_tracks"]["cpp"]["slug"] == "cpk_01"
    assert showcase["language_tracks"]["pascal"]["slug"] == "psk_01"
    assert showcase["language_tracks"]["python"]["slug"] == "pyk_01"

    overview = task_row_to_overview(row, target_language="cpp")
    assert set(overview["available_language_tracks"]) == {"pascal", "python", "cpp"}
    assert overview["pedagogical_slot_id"] == "psk_01"
    assert overview["slot_id"] == "cpk_01"


def test_cpp_group_c_separate_tasks(db_session: Session):
    showcase = normalize_unified_showcase(_cpp_track("cpk_12", "cpp_entry"))
    showcase["pedagogical_slot_id"] = "cpk_12"
    _add_task(db_session, task_id=10, title="[C++ v1: Include]", showcase=showcase)
    overview = task_row_to_overview(
        db_session.query(TaskModel).filter_by(id=10).one(),
        target_language="cpp",
    )
    assert overview["pedagogical_slot_id"] == "cpk_12"
    assert overview["available_language_tracks"] == ["cpp"]
    assert is_cpp_only_slot("cpk_12")
    assert "cpk_12" in CPP_ONLY_SLOTS


def test_cpp_detail_returns_cpp_payload(db_session: Session):
    merged = merge_showcase_pair(
        _showcase(slug="psk_09", language="pascal", chapter="program_skeleton", ped_id="psk_09"),
        _showcase(slug="pyk_08", language="python", chapter="program_entry"),
        pedagogical_slot_id="psk_09",
    )
    cpp_track = _cpp_track("cpk_08", "cpp_entry")
    cpp_track["educational_goal"] = "C++ comments goal"
    merged = merge_language_track(merged, cpp_track, "cpp")
    merged = normalize_unified_showcase(merged)
    _add_task(db_session, task_id=20, title="Comments unified", showcase=merged)

    payload = {
        "id": 20,
        "title": "Comments",
        "description": "Pascal goal",
        "code_examples": {"curriculum_showcase": merged},
    }
    result = apply_learning_language_to_payload(payload, "cpp", showcase=merged)
    assert result.get("target_language") == "cpp"
    assert result.get("description") == "C++ comments goal"
    resolved = result["code_examples"]["curriculum_showcase"]
    assert resolved["slug"] == "cpk_08"


def test_cpp_no_duplicate_pedagogical_slot_id(db_session: Session):
    merged = merge_showcase_pair(
        _showcase(slug="psk_02", language="pascal", chapter="program_skeleton"),
        _showcase(slug="pyk_02", language="python", chapter="program_entry"),
        pedagogical_slot_id="psk_02",
    )
    merged = merge_language_track(merged, _cpp_track("cpk_02", "cpp_entry"), "cpp")
    merged = normalize_unified_showcase(merged)
    _add_task(db_session, task_id=30, title="Unified triple", showcase=merged)
    errors = validate_no_duplicate_pedagogical_slot_ids(db_session)
    assert not errors


@pytest.fixture
def api_client(db_session: Session) -> Iterator[TestClient]:
    def _override_get_db() -> Iterator[Session]:
        yield db_session

    def _allowed_task_ids(db: Session, _current) -> set[int]:
        return {int(row.id) for row in db.query(TaskModel).filter_by(is_delete=False).all()}

    app.dependency_overrides[get_db] = _override_get_db
    with patch("api.tasks.endpoints.list_tasks._allowed_task_ids", _allowed_task_ids):
        client = TestClient(app)
        try:
            yield client
        finally:
            app.dependency_overrides.clear()


def test_cpp_overview_shows_available_track(api_client: TestClient, db_session: Session):
    merged = merge_showcase_pair(
        _showcase(slug="typ_01", language="pascal", chapter="typed_variables"),
        _showcase(slug="pyt_01", language="python", chapter="typed_variables"),
        pedagogical_slot_id="typ_01",
    )
    merged = merge_language_track(merged, _cpp_track("cpt_01", "cpp_types"), "cpp")
    merged = normalize_unified_showcase(merged)
    _add_task(db_session, task_id=40, title="Types triple", showcase=merged)

    response = api_client.get("/tasks/overview", params={"target_language": "cpp"})
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    item = body["tasks"][0]
    assert item["pedagogical_slot_id"] == "typ_01"
    assert "cpp" in item["available_language_tracks"]
    assert item["slot_id"] == "cpt_01"


def test_cpp_language_neutral_metadata():
    for rec in all_v311_task_records():
        for value in (rec.title, rec.educational_goal):
            assert not LANG_PATTERN.search(value), f"{rec.slot_id}: {value}"
