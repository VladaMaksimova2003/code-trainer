"""Unit tests - curriculum next-task selection and collection ordering."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from application.curriculum.collections.curriculum_next_service import (
    NEXT_TASK_ACTION_ORDER,
    _sort_collection_summaries,
    build_curriculum_collections_view,
    build_global_curriculum_next,
    build_pascal_conditions_showcase_next,
    build_pascal_loops_showcase_next,
    order_conditions_showcase_tasks,
    order_loops_showcase_tasks,
)
from application.curriculum.pascal.showcase.pascal_showcase_all_specs import all_pascal_showcase_specs
from application.curriculum.pascal.showcase.pascal_showcase_core import (
    list_showcase_tasks_for_collection,
    seed_pascal_showcase_collection,
)
from application.curriculum.pascal.showcase.pascal_showcase_next import order_collection_showcase_tasks
from application.curriculum.pascal.showcase.pascal_showcase_registry import PASCAL_SHOWCASE_COLLECTIONS
from application.curriculum.pascal.showcase.pascal_v311_registry import PASCAL_V311_SHOWCASE_COLLECTIONS
from application.curriculum.pascal.showcase.pascal_v311_showcase_all_specs import all_pascal_v311_showcase_specs
from application.curriculum.pascal.catalog.pascal_curriculum_v3_catalog import V311_TOTAL_TASKS
from application.curriculum.progress.student_curriculum_progress_service import (
    StudentCurriculumProgressService,
)
from infrastructure.db.models.base import Base
from infrastructure.db.models.learning.curriculum_chapter_meta import CurriculumChapterMeta
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
            CurriculumChapterMeta.__table__,
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


def _seed_pascal_track(session: Session) -> None:
    specs = all_pascal_showcase_specs()
    for col in PASCAL_SHOWCASE_COLLECTIONS:
        seed_pascal_showcase_collection(session, col.chapter_key, specs[col.chapter_key])
    v311_specs = all_pascal_v311_showcase_specs()
    for col in PASCAL_V311_SHOWCASE_COLLECTIONS:
        if col.chapter_key in v311_specs:
            seed_pascal_showcase_collection(session, col.chapter_key, v311_specs[col.chapter_key])
    session.commit()


def _seed_both(session: Session) -> None:
    """Seed full Pascal track (all 14 showcase collections)."""
    _seed_pascal_track(session)


def _ordered_slugs(session: Session, *, collection: str) -> list[str]:
    specs = all_pascal_showcase_specs()
    if collection == "conditions":
        return [row["slug"] for row in order_conditions_showcase_tasks(session)]
    if collection == "loops":
        return [row["slug"] for row in order_loops_showcase_tasks(session)]
    if collection == "variables_and_io":
        return [
            row["slug"]
            for row in order_collection_showcase_tasks(
                session, "variables_and_io", specs["variables_and_io"]
            )
        ]
    return [
        row["slug"]
        for row in list_showcase_tasks_for_collection(session, collection)
    ]


def _record(session: Session, user_id: int, task_id: int, *, passed: bool) -> None:
    sub = Submission(
        user_id=user_id,
        task_id=task_id,
        language="pascal",
        code="begin end.",
        status="done",
        success=passed,
    )
    session.add(sub)
    session.flush()
    StudentCurriculumProgressService(session).record_submission_result(
        user_id, sub.id, task_id, passed=passed
    )
    session.commit()


def test_next_task_action_order_follows_pedagogical_study_path():
    assert NEXT_TASK_ACTION_ORDER[0] == "assemble"
    assert NEXT_TASK_ACTION_ORDER.index("debug") > NEXT_TASK_ACTION_ORDER.index("assemble")
    assert NEXT_TASK_ACTION_ORDER.index("translate") > NEXT_TASK_ACTION_ORDER.index("debug")


def test_sort_collection_summaries_follows_chapter_sort_order(monkeypatch, db_session: Session):
    from application.curriculum.chapters import curriculum_chapter_meta_service as meta

    monkeypatch.setattr(
        meta,
        "list_chapters",
        lambda session, language=None, meta_ctx=None: [
            meta.ChapterMetaRecord(
                language="python",
                chapter_key="algo_basics",
                title="1. Basics",
                description="",
                sort_order=0,
                is_custom=False,
            ),
            meta.ChapterMetaRecord(
                language="python",
                chapter_key="aggregation",
                title="9. Aggregation",
                description="",
                sort_order=80,
                is_custom=False,
            ),
        ],
    )
    summaries = [
        {"chapter_key": "aggregation", "title_ru": "9. Aggregation"},
        {"chapter_key": "algo_basics", "title_ru": "1. Basics"},
    ]
    ordered = _sort_collection_summaries(db_session, summaries, language="python")
    assert [item["chapter_key"] for item in ordered] == ["algo_basics", "aggregation"]


def test_conditions_baseline_next_is_first_task_in_study_order(db_session: Session):
    _seed_both(db_session)

    user_id = db_session.query(User).first().id
    payload = build_pascal_conditions_showcase_next(db_session, user_id)

    assert payload["completed"] is False
    assert payload["button_label"] == "Начать сборник"
    assert payload["next_task"]["slug"] == "simple_branch_asm_blocks"
    assert payload["progress"]["passed_tasks"] == 0


def test_loops_baseline_next_is_first_task_in_study_order(db_session: Session):
    _seed_both(db_session)

    user_id = db_session.query(User).first().id
    payload = build_pascal_loops_showcase_next(db_session, user_id)

    assert payload["completed"] is False
    assert payload["next_task"]["slug"] == "counted_loop_asm_blocks"


def test_after_first_passed_next_moves_to_second_in_tc(db_session: Session):
    _seed_both(db_session)

    user_id = db_session.query(User).first().id
    ordered = order_loops_showcase_tasks(db_session)
    first_id = ordered[0]["task_id"]
    _record(db_session, user_id, first_id, passed=True)

    payload = build_pascal_loops_showcase_next(db_session, user_id)
    assert payload["next_task"]["slug"] == ordered[1]["slug"]
    assert payload["button_label"] == "Продолжить сборник"
    assert payload["progress"]["passed_tasks"] == 1


def test_failed_task_remains_next(db_session: Session):
    _seed_both(db_session)

    user_id = db_session.query(User).first().id
    ordered = order_conditions_showcase_tasks(db_session)
    first_id = ordered[0]["task_id"]
    _record(db_session, user_id, first_id, passed=True)

    second_id = ordered[1]["task_id"]
    _record(db_session, user_id, second_id, passed=False)

    payload = build_pascal_conditions_showcase_next(db_session, user_id)
    assert payload["next_task"]["task_id"] == second_id
    assert payload["next_task"]["progress_status"] == "failed"
    assert payload["progress"]["passed_tasks"] == 1


def test_all_conditions_passed_marks_completed(db_session: Session):
    _seed_both(db_session)

    user_id = db_session.query(User).first().id
    for row in order_conditions_showcase_tasks(db_session):
        _record(db_session, user_id, row["task_id"], passed=True)

    payload = build_pascal_conditions_showcase_next(db_session, user_id)
    assert payload["completed"] is True
    assert payload["progress"]["passed_tasks"] == 12
    assert payload["next_task"]["slug"] == _ordered_slugs(db_session, collection="conditions")[0]


def test_global_next_starts_with_variables_and_io(db_session: Session):
    _seed_both(db_session)

    user_id = db_session.query(User).first().id
    first_col = PASCAL_V311_SHOWCASE_COLLECTIONS[0]
    v311_specs = all_pascal_v311_showcase_specs()
    first_slug = order_collection_showcase_tasks(
        db_session, first_col.chapter_key, v311_specs[first_col.chapter_key]
    )[0]["slug"]
    payload = build_global_curriculum_next(db_session, user_id)
    assert payload["collection"]["collection_id"] == first_col.collection_id
    assert payload["next_task"]["slug"] == first_slug
    assert payload["button_label"] == "Начать обучение"


def test_global_next_moves_to_conditions_after_variables_and_io_complete(db_session: Session):
    _seed_both(db_session)

    user_id = db_session.query(User).first().id
    v311_specs = all_pascal_v311_showcase_specs()
    for row in order_collection_showcase_tasks(
        db_session, "algo_basics", v311_specs["algo_basics"]
    ):
        _record(db_session, user_id, row["task_id"], passed=True)

    payload = build_global_curriculum_next(db_session, user_id)
    assert payload["completed"] is False
    assert payload["next_task"] is not None
    assert payload["collection"]["chapter_key"] in {"algo_basics", "branches"}


def test_global_next_moves_to_loops_after_conditions_complete(db_session: Session):
    _seed_both(db_session)

    user_id = db_session.query(User).first().id
    v311_specs = all_pascal_v311_showcase_specs()
    for chapter in ("algo_basics", "branches"):
        for row in order_collection_showcase_tasks(db_session, chapter, v311_specs[chapter]):
            _record(db_session, user_id, row["task_id"], passed=True)

    payload = build_global_curriculum_next(db_session, user_id)
    assert payload["completed"] is False
    assert payload["next_task"] is not None
    assert payload["collection"]["chapter_key"] in {"algo_basics", "branches", "loops"}


def test_collections_groups_by_language_with_all_pascal_collections(db_session: Session):
    _seed_both(db_session)

    user_id = db_session.query(User).first().id
    v311_specs = all_pascal_v311_showcase_specs()
    first_col = PASCAL_V311_SHOWCASE_COLLECTIONS[0]
    first_ordered = order_collection_showcase_tasks(
        db_session, first_col.chapter_key, v311_specs[first_col.chapter_key]
    )
    _record(db_session, user_id, first_ordered[0]["task_id"], passed=True)

    payload = build_curriculum_collections_view(db_session, user_id)
    assert len(payload["languages"]) == 5

    pascal = next(lang for lang in payload["languages"] if lang["language"] == "pascal")
    assert pascal["available"] is True
    assert pascal["progress"]["total_tasks"] >= V311_TOTAL_TASKS
    assert pascal["progress"]["passed_tasks"] == 1
    assert len(pascal["collections"]) == len(PASCAL_V311_SHOWCASE_COLLECTIONS)

    first = pascal["collections"][0]
    branches = next(c for c in pascal["collections"] if c["chapter_key"] == "branches")
    loops = next(c for c in pascal["collections"] if c["chapter_key"] == "loops")

    assert first["chapter_key"] == first_col.chapter_key
    assert first["progress"]["passed_tasks"] == 1

    assert branches["chapter_key"] == "branches"
    assert branches["progress"]["passed_tasks"] == 0

    assert loops["chapter_key"] == "loops"
    assert loops["progress"]["passed_tasks"] == 0

    python = next(lang for lang in payload["languages"] if lang["language"] == "python")
    assert python["available"] is True
    assert len(python["collections"]) == len(PASCAL_V311_SHOWCASE_COLLECTIONS)

    assert len(payload["collections"]) == len(PASCAL_V311_SHOWCASE_COLLECTIONS) * len(payload["languages"])

