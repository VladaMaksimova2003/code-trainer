"""Unit tests — Universal Core merge and pedagogical task model."""

from __future__ import annotations

from collections.abc import Iterator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from application.curriculum.mirror.curriculum_slot_mirror_map import (
    PYTHON_ONLY_CHAPTERS,
    all_mirrored_pairs,
)
from application.curriculum.mirror.pedagogical_task_model import (
    FORBIDDEN_PRIMARY_ACTIONS,
    FORBIDDEN_TASK_FORMATS,
    merge_showcase_pair,
    normalize_unified_showcase,
)
from application.curriculum.mirror.pedagogical_task_store import (
    apply_learning_language_to_payload,
    pedagogical_slot_id_from_showcase,
)
from application.curriculum.mirror.universal_core_validation import (
    run_all_validations,
    validate_no_duplicate_pedagogical_slot_ids,
)
from application.tasks.services.catalog.task_overview import list_task_overviews, task_row_to_overview
from infrastructure.db.models.base import Base
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.task.task import Task as TaskModel
from main import app
from infrastructure.db.session import get_db

load_models()


def _showcase(
    *,
    slug: str,
    language: str,
    chapter: str,
    ped_id: str | None = None,
    tracks: dict | None = None,
) -> dict:
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
    if tracks:
        base["language_tracks"] = tracks
    return base


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


def _add_task(
    session: Session,
    *,
    task_id: int,
    title: str,
    showcase: dict,
    deleted: bool = False,
) -> TaskModel:
    row = TaskModel(
        id=task_id,
        title=title,
        description="detail",
        task_type="task_translate_fragment",
        difficulty="easy",
        is_delete=deleted,
        code_examples={"curriculum_showcase": showcase, "patterns": ["loop_for"]},
    )
    session.add(row)
    session.commit()
    return row


def test_merge_showcase_pair_psk_09_pyk_08():
    merged = merge_showcase_pair(
        _showcase(slug="psk_09", language="pascal", chapter="program_skeleton"),
        _showcase(slug="pyk_08", language="python", chapter="program_entry"),
        pedagogical_slot_id="psk_09",
    )
    assert merged["pedagogical_slot_id"] == "psk_09"
    assert merged["language_tracks"]["pascal"]["slug"] == "psk_09"
    assert merged["language_tracks"]["python"]["slug"] == "pyk_08"


def test_mirror_pairs_are_merged(db_session: Session):
    pair = ("psk_01", "pyk_01")
    if pair not in all_mirrored_pairs().items():
        pytest.skip("pair not in mirror map")
    pascal_slot, python_slot = pair
    merged = merge_showcase_pair(
        _showcase(slug=pascal_slot, language="pascal", chapter="program_skeleton"),
        _showcase(slug=python_slot, language="python", chapter="program_entry"),
        pedagogical_slot_id=pascal_slot,
    )
    _add_task(
        db_session,
        task_id=1,
        title="[Pascal v3.1.1: Unified]",
        showcase=merged,
    )
    _add_task(
        db_session,
        task_id=2,
        title="[Python v1: Duplicate]",
        showcase=_showcase(slug=python_slot, language="python", chapter="program_entry"),
        deleted=True,
    )
    errors = validate_no_duplicate_pedagogical_slot_ids(db_session)
    assert not errors
    overview = list_task_overviews(db_session, allowed_task_ids=None)
    ped_ids = [t["pedagogical_slot_id"] for t in overview["tasks"]]
    assert ped_ids.count(pascal_slot) == 1


def test_no_duplicate_pedagogical_slot_ids(db_session: Session):
    showcase = merge_showcase_pair(
        _showcase(slug="psk_02", language="pascal", chapter="program_skeleton"),
        _showcase(slug="pyk_02", language="python", chapter="program_entry"),
        pedagogical_slot_id="psk_02",
    )
    _add_task(db_session, task_id=1, title="Unified", showcase=showcase)
    _add_task(
        db_session,
        task_id=2,
        title="Duplicate",
        showcase={**showcase, "slug": "psk_02"},
    )
    errors = validate_no_duplicate_pedagogical_slot_ids(db_session)
    assert len(errors) == 1
    assert "psk_02" in errors[0]


def test_group_c_not_merged(db_session: Session):
    _add_task(
        db_session,
        task_id=10,
        title="Python comprehension",
        showcase=_showcase(slug="pycmp_01", language="python", chapter="comprehensions"),
    )
    _add_task(
        db_session,
        task_id=11,
        title="Python exception",
        showcase=_showcase(slug="pyex_01", language="python", chapter="exceptions"),
    )
    validation = run_all_validations(db_session)
    assert not validation["group_c_incorrectly_merged"]


def test_python_only_slot_has_single_track(db_session: Session):
    showcase = _showcase(slug="pyt_05", language="python", chapter="typed_variables")
    showcase["pedagogical_slot_id"] = "pyt_05"
    _add_task(db_session, task_id=20, title="None literal", showcase=showcase)
    overview = task_row_to_overview(
        db_session.query(TaskModel).filter_by(id=20).one(),
        target_language="python",
    )
    assert overview["available_language_tracks"] == ["python"]
    assert overview["pedagogical_slot_id"] == "pyt_05"


def test_overview_shows_available_language_tracks(db_session: Session):
    merged = normalize_unified_showcase(
        merge_showcase_pair(
            _showcase(slug="cnd_01", language="pascal", chapter="conditions"),
            _showcase(slug="pyc_01", language="python", chapter="conditions"),
            pedagogical_slot_id="cnd_01",
        )
    )
    _add_task(db_session, task_id=30, title="If else", showcase=merged)
    overview = list_task_overviews(
        db_session,
        allowed_task_ids=None,
        target_language="python",
    )
    item = overview["tasks"][0]
    assert item["available_language_tracks"] == ["pascal", "python"]
    assert item["pedagogical_slot_id"] == "cnd_01"
    assert item["slot_id"] == "pyc_01"
    assert item["target_language"] == "python"


def test_python_and_pascal_share_universal_core_slots(db_session: Session):
    merged = merge_showcase_pair(
        _showcase(slug="typ_02", language="pascal", chapter="typed_variables"),
        _showcase(slug="pyt_02", language="python", chapter="typed_variables"),
        pedagogical_slot_id="typ_02",
    )
    _add_task(db_session, task_id=40, title="Assignment", showcase=merged)
    ped = pedagogical_slot_id_from_showcase(merged)
    assert ped == "typ_02"
    tracks = merged["language_tracks"]
    assert tracks["pascal"]["exercise_pattern_id"] == "tr_typ_02"
    assert tracks["python"]["exercise_pattern_id"] == "tr_pyt_02"


def test_no_analyze_tasks(db_session: Session):
    showcase = _showcase(slug="psk_99", language="pascal", chapter="program_skeleton")
    showcase["primary_action"] = next(iter(FORBIDDEN_PRIMARY_ACTIONS))
    _add_task(db_session, task_id=51, title="Bad action", showcase=showcase)
    validation = run_all_validations(db_session)
    assert len(validation["forbidden_formats"]) >= 1


def test_no_matching_format(db_session: Session):
    showcase = _showcase(slug="psk_98", language="pascal", chapter="program_skeleton")
    showcase["task_format"] = next(iter(FORBIDDEN_TASK_FORMATS))
    _add_task(db_session, task_id=61, title="Bad format", showcase=showcase)
    validation = run_all_validations(db_session)
    assert len(validation["forbidden_formats"]) >= 1


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


def test_task_detail_returns_selected_language_track(api_client: TestClient, db_session: Session):
    merged = merge_showcase_pair(
        _showcase(
            slug="psk_09",
            language="pascal",
            chapter="program_skeleton",
            ped_id="psk_09",
        ),
        _showcase(
            slug="pyk_08",
            language="python",
            chapter="program_entry",
        ),
        pedagogical_slot_id="psk_09",
    )
    merged["language_tracks"]["python"]["educational_goal"] = "Python comments goal"
    _add_task(db_session, task_id=70, title="Comments", showcase=merged)
    payload = {
        "id": 70,
        "title": "Comments",
        "description": "Pascal goal",
        "code_examples": {"curriculum_showcase": merged},
    }
    result = apply_learning_language_to_payload(payload, "python", showcase=merged)
    assert result.get("target_language") == "python"
    assert result.get("description") == "Python comments goal"
    showcase = result["code_examples"]["curriculum_showcase"]
    assert showcase["slug"] == "pyk_08"


def test_overview_endpoint_language_tracks(api_client: TestClient, db_session: Session):
    merged = merge_showcase_pair(
        _showcase(slug="lop_01", language="pascal", chapter="loops"),
        _showcase(slug="pyl_01", language="python", chapter="loops"),
        pedagogical_slot_id="lop_01",
    )
    _add_task(db_session, task_id=80, title="For loop", showcase=merged)
    response = api_client.get(
        "/tasks/overview",
        params={"target_language": "python", "course": "python"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    item = body["tasks"][0]
    assert item["pedagogical_slot_id"] == "lop_01"
    assert "python" in item["available_language_tracks"]
    assert item["slot_id"] == "pyl_01"


def test_attach_curriculum_display_pedagogical_fields(db_session: Session):
    merged = merge_showcase_pair(
        _showcase(slug="psk_01", language="pascal", chapter="program_skeleton"),
        _showcase(slug="pyk_01", language="python", chapter="program_entry"),
        pedagogical_slot_id="psk_01",
    )
    from application.curriculum.display.curriculum_labels import _attach_pedagogical_metadata

    payload = _attach_pedagogical_metadata(
        {"id": 90, "title": "Entry", "code_examples": {}},
        merged,
        learning_language="python",
    )
    assert payload["pedagogical_slot_id"] == "psk_01"
    assert payload["available_language_tracks"] == ["pascal", "python"]
    assert payload["concept_id"] == "program_entry"
