"""Flowchart slot replacements - seed, API payload, validation smoke."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from application.curriculum.pascal.catalog.pascal_flowchart_diagrams import diagram_for_sum_n, diagram_if_n_pos
from application.curriculum.pascal.catalog.pascal_flowchart_slot_replacements import FLOWCHART_SLOT_BY_ID
from application.curriculum.pascal.showcase.pascal_showcase_all_specs import all_pascal_showcase_specs
from application.curriculum.pascal.showcase.pascal_showcase_core import (
    list_showcase_tasks_for_collection,
    seed_pascal_showcase_collection,
)
from application.curriculum.pascal.showcase.pascal_showcase_registry import PASCAL_SHOWCASE_COLLECTIONS
from application.execution.block_reorder_validation import validate_block_reorder_structural
from application.execution.services.flow_validation_service import FlowValidationService
from application.tasks.services.block_reorder_helpers import build_entity_from_db
from application.tasks.services.catalog.task_query import TaskQueryService
from application.tasks.use_cases.block_reorder.get import get_block_reorder_public_task
from infrastructure.db.models.base import Base
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.task.task import BlockReorderTask, Task as TaskModel
from infrastructure.db.models.task.task import TranslationTask
from infrastructure.db.models.task.task_curriculum_link import TaskCurriculumLinkModel


@pytest.fixture
def db_session() -> Session:
    load_models()
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(
        engine,
        tables=[
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


def _seed_all(session: Session) -> None:
    specs = all_pascal_showcase_specs()
    for col in PASCAL_SHOWCASE_COLLECTIONS:
        seed_pascal_showcase_collection(session, col.chapter_key, specs[col.chapter_key])
    session.commit()


def _task_by_slot_id(session: Session, slot_id: str) -> TaskModel:
    for row in session.scalars(select(TaskModel)).all():
        meta = (row.code_examples or {}).get("curriculum_showcase") or {}
        if meta.get("slot_id") == slot_id:
            return row
    raise AssertionError(f"Task not found for slot_id={slot_id}")


def test_flowchart_slots_seed_102_tasks(db_session: Session):
    _seed_all(db_session)
    total = sum(
        len(list_showcase_tasks_for_collection(db_session, col.chapter_key))
        for col in PASCAL_SHOWCASE_COLLECTIONS
    )
    assert total == 102


@pytest.mark.parametrize("slot_id", sorted(FLOWCHART_SLOT_BY_ID.keys()))
def test_flowchart_slot_payload_and_validation(db_session: Session, slot_id: str):
    _seed_all(db_session)
    slot = FLOWCHART_SLOT_BY_ID[slot_id]
    row = _task_by_slot_id(db_session, slot_id)
    mode = (slot.extra or {}).get("flowchart_mode")
    query = TaskQueryService()
    public = query.get_task(db_session, row.id) or get_block_reorder_public_task(
        db_session, row.id
    )
    assert public is not None

    if mode == "flowchart_to_code":
        assert public["type"] in {"task_flowchart_to_code", "blocks", "diagram"}
        assert public["diagram"]["nodes"]
        assert any(
            str(n.get("text") or "").strip() and str(n.get("text")) != "заголовок?"
            for n in public["diagram"]["nodes"]
        )
        ref = (slot.extra or {}).get("reference_code_pascal", "")
        assert ref.strip()
        assert public.get("test_cases")

    elif mode == "code_to_flowchart":
        assert public["type"] in {"task_flowchart_to_code", "blocks", "diagram"}
        assert public.get("code_examples", {}).get("pascal")
        assert public["flow_spec"].get("required_sequence")
        assert public["flow_spec"].get("required_text_checks")
        service = FlowValidationService()
        reference_diagram = {
            "cond_s01": diagram_if_n_pos(),
            "loop_s01": diagram_for_sum_n(),
        }[slot_id]
        nodes = reference_diagram["nodes"]
        edges = reference_diagram["edges"]
        for node in nodes:
            node.setdefault("x", node.get("position", {}).get("x", 0))
            node.setdefault("y", node.get("position", {}).get("y", 0))
        flow_spec = public["flow_spec"]
        result = service.validate_with_details(
            flow=[],
            flow_spec=flow_spec,
            task=public,
            nodes=nodes,
            edges=edges,
        )
        assert result["errors"] == [], result["errors"]

        wrong_nodes = [
            {**nodes[0]},
            {**nodes[1]},
            {**nodes[-1]},
        ]
        wrong_edges = [
            {"source": wrong_nodes[0]["id"], "target": wrong_nodes[1]["id"]},
            {"source": wrong_nodes[1]["id"], "target": wrong_nodes[2]["id"]},
        ]
        wrong = service.validate_with_details(
            flow=[],
            flow_spec=flow_spec,
            task=public,
            nodes=wrong_nodes,
            edges=wrong_edges,
        )
        assert wrong["errors"], wrong["errors"]

    elif mode == "flowchart_to_blocks":
        payload = get_block_reorder_public_task(db_session, row.id)
        assert payload is not None
        assert payload["diagram"]["nodes"]
        entity = build_entity_from_db(row, row.block_reorder_task)
        correct_order = list(payload["correct_order"])
        assembled = entity.build_code(correct_order, payload["language"], None)
        check = validate_block_reorder_structural(
            db_session,
            row.id,
            order=correct_order,
            language=payload["language"],
            assembled_code=assembled,
        )
        assert check is not None
        assert check["structural_correct"] is True

    else:
        pytest.fail(f"Unknown flowchart_mode: {mode}")
