"""Integration - Pascal curriculum showcase reset, seed, and execution smoke tests."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from application.curriculum.pascal.legacy.loops.loops_showcase_data import loops_showcase_specs
from application.curriculum.pascal.legacy.loops.loops_showcase_seeder import (
    find_showcase_task_by_slug,
    list_showcase_tasks,
    seed_pascal_loops_showcase,
)
from application.curriculum.pascal.dev.showcase_dev_reset import apply_showcase_dev_reset, plan_showcase_dev_reset
from application.curriculum.task_curriculum_link_service import TaskCurriculumLinkService
from infrastructure.db.models.base import Base
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.task.task import BlockReorderTask, Task as TaskModel
from infrastructure.db.models.task.task import TranslationTask
from infrastructure.db.models.task.task_curriculum_link import TaskCurriculumLinkModel
from infrastructure.db.models.user.user import User


@pytest.fixture
def showcase_db() -> Session:
    load_models()
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
            User.__table__,
            TaskModel.__table__,
            TranslationTask.__table__,
            BlockReorderTask.__table__,            TaskCurriculumLinkModel.__table__,
        ],
    )
    session = sessionmaker(bind=engine)()
    try:
        yield session
    finally:
        session.close()


def test_reset_plan_keeps_only_pascal_curriculum_showcase(showcase_db: Session):
    seed_pascal_loops_showcase(showcase_db)
    showcase_db.commit()

    legacy = TaskModel(
        title="Legacy demo task",
        description="old",
        task_type="task_translate_snippet",
        difficulty="easy",
        test_cases=[],
        code_examples={},
        flow_spec={},
    )
    showcase_db.add(legacy)
    showcase_db.commit()

    plan = plan_showcase_dev_reset(showcase_db)
    assert len(plan.keep) == 7
    assert len(plan.delete) == 1
    assert plan.delete[0].title == "Legacy demo task"


def test_reset_apply_removes_legacy_and_keeps_showcase(showcase_db: Session):
    seed_pascal_loops_showcase(showcase_db)
    showcase_db.commit()
    showcase_db.add(
        TaskModel(
            title="Old showcase demo",
            description="x",
            task_type="task_translate_snippet",
            difficulty="easy",
            test_cases=[],
            code_examples={},
            flow_spec={},
        )
    )
    showcase_db.commit()

    report = apply_showcase_dev_reset(showcase_db, dry_run=False)
    showcase_db.commit()

    assert len(report.deleted_task_ids) == 1
    remaining = showcase_db.scalars(select(TaskModel)).all()
    assert len(remaining) == 7
    assert all(
        (row.code_examples or {}).get("curriculum_showcase", {}).get("group")
        == "pascal_curriculum_loops_v1"
        for row in remaining
    )


def test_full_cycle_reset_seed_seven_primary_links(showcase_db: Session):
    seed_pascal_loops_showcase(showcase_db)
    showcase_db.commit()
    showcase_db.add(
        TaskModel(
            title="Extra legacy",
            description="x",
            task_type="task_translate_snippet",
            difficulty="easy",
            test_cases=[],
            code_examples={},
            flow_spec={},
        )
    )
    showcase_db.commit()

    apply_showcase_dev_reset(showcase_db, dry_run=False)
    showcase_db.commit()

    seed_report = seed_pascal_loops_showcase(showcase_db)
    showcase_db.commit()

    assert seed_report.errors == []
    tasks = list_showcase_tasks(showcase_db)
    assert len(tasks) == 7
    for item in tasks:
        assert item["has_primary_link"] is True
        assert item["learning_concept_id"] == "loops"


def test_curriculum_metadata_available_after_seed(showcase_db: Session):
    seed_pascal_loops_showcase(showcase_db)
    showcase_db.commit()
    svc = TaskCurriculumLinkService(showcase_db)

    for spec in loops_showcase_specs():
        task = find_showcase_task_by_slug(showcase_db, spec.slug)
        assert task is not None
        meta = svc.get_task_curriculum_metadata(task.id)
        assert meta["has_curriculum_link"] is True
        primary = meta["primary_link"]
        assert primary["technical_concept_id"] == spec.technical_concept_id
        assert primary["exercise_pattern_id"] == spec.exercise_pattern_id
        assert primary["action"]

