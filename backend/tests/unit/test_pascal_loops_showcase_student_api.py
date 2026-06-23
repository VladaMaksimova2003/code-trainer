"""Unit tests — Pascal loops showcase student API payload."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from application.curriculum.display.curriculum_labels import (
    ACTION_DESCRIPTIONS_RU,
    ACTION_LABELS,
    ACTION_SKILL_LABELS_RU,
)
from application.curriculum.pascal.legacy.loops.loops_showcase_data import TITLE_PREFIX
from application.curriculum.pascal.legacy.loops.loops_showcase_seeder import seed_pascal_loops_showcase
from application.curriculum.pascal.legacy.loops.loops_showcase_student import build_pascal_loops_showcase_student_view
from application.curriculum.display.showcase_display import SHOWCASE_TITLE_PREFIXES
from application.tasks.services.catalog.task_query import TaskQueryService
from infrastructure.db.models.base import Base
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.task.task import BlockReorderTask, Task as TaskModel
from infrastructure.db.models.task.task import TranslationTask
from infrastructure.db.models.task.task_curriculum_link import TaskCurriculumLinkModel
from infrastructure.db.models.user.user import User

EXPECTED_TC_ORDER = [
    "counted_loop",
    "pre_condition_loop",
    "post_condition_loop",
    "collection_iteration",
    "nested_iteration",
    "loop_control",
]


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
            BlockReorderTask.__table__,
            TaskCurriculumLinkModel.__table__,
        ],
    )
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


def test_student_view_returns_seven_tasks_in_tc_order(db_session: Session):
    seed_pascal_loops_showcase(db_session)
    db_session.commit()

    payload = build_pascal_loops_showcase_student_view(db_session)

    assert payload["learning_concept"]["id"] == "loops"
    assert payload["learning_concept"]["name_ru"] == "Циклы"
    assert payload["study_order_tc"] == EXPECTED_TC_ORDER
    assert payload["total_tasks"] == 7


def test_student_cards_include_readable_labels(db_session: Session):
    seed_pascal_loops_showcase(db_session)
    db_session.commit()

    payload = build_pascal_loops_showcase_student_view(db_session)
    sample = payload["technical_concepts"][0]["tasks"][0]

    assert sample["technical_concept_name_ru"] == "For to/downto"
    assert sample["action_label"] == "Перенести"
    assert sample["action_skill_label"] == "Перенести на Pascal"
    assert sample["action_description_ru"] == ACTION_DESCRIPTIONS_RU["translate"]
    assert sample["title"] == "Цикл for: перевод с Python на Pascal"
    assert sample["short_instruction"]
    assert "exercise_pattern_id" not in sample
    assert "exercise_pattern_label" not in sample
    assert "learning_concept_id" not in sample

    assert payload["labels"]["actions"]["translate"]["badge"] == "Перенести"
    assert payload["labels"]["actions"]["translate"]["skill"] == ACTION_SKILL_LABELS_RU["translate"]
    assert "exercise_patterns" not in payload["labels"]


def test_each_task_has_student_facing_title_without_showcase_prefix(db_session: Session):
    seed_pascal_loops_showcase(db_session)
    db_session.commit()

    payload = build_pascal_loops_showcase_student_view(db_session)
    for tc in payload["technical_concepts"]:
        for task in tc["tasks"]:
            assert task["action"] in ACTION_LABELS
            assert task["action_label"] == ACTION_LABELS[task["action"]]
            assert task["title"]
            for prefix in SHOWCASE_TITLE_PREFIXES:
                assert not task["title"].startswith(prefix)
            assert not task["title"].startswith(TITLE_PREFIX)


def test_showcase_task_detail_includes_curriculum_header(db_session: Session):
    seed_pascal_loops_showcase(db_session)
    db_session.commit()

    payload = build_pascal_loops_showcase_student_view(db_session)
    task_id = payload["technical_concepts"][0]["tasks"][0]["task_id"]
    loaded = TaskQueryService().get_task(db_session, task_id)

    assert loaded is not None
    assert loaded["title"] == "Цикл for: перевод с Python на Pascal"
    curriculum = loaded["curriculum"]
    assert curriculum["context_line_ru"] == "Pascal · Циклы · For to/downto"
    assert curriculum["theme_name_ru"] == "Циклы"
    assert curriculum["subtopic_name_ru"] == "For to/downto"
    assert curriculum["action_skill_label"] == "Перенести на Pascal"
    assert curriculum["instruction_ru"] == ACTION_DESCRIPTIONS_RU["translate"]
    if "navigation" in curriculum:
        assert curriculum["navigation"]["total_tasks"] == 7
        assert curriculum["navigation"]["task_index"] == 1
    assert "exercise_pattern_id" not in curriculum
    assert "learning_concept_id" not in curriculum
    assert "skill_line_ru" not in curriculum


def test_legacy_task_without_curriculum_link_unchanged(db_session: Session):
    legacy = TaskModel(
        title="Legacy without curriculum",
        description="unchanged",
        task_type="task_translate_snippet",
        difficulty="easy",
        test_cases=[],
        code_examples={},
        flow_spec={},
    )
    db_session.add(legacy)
    db_session.commit()

    payload = TaskQueryService().get_task(db_session, legacy.id)
    assert payload is not None
    assert payload["title"] == "Legacy without curriculum"
    assert "curriculum" not in payload or payload.get("curriculum") is None
