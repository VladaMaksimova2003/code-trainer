"""Use case: create block-reorder / code-assembly task."""
from __future__ import annotations

from typing import Any

import sqlalchemy as sa
from sqlalchemy.orm import Session

from application.tasks.services.block_reorder_helpers import (
    build_canonical_code,
    build_shuffled_blocks,
    autogenerate_test_cases,
    parse_difficulty,
)
from application.tasks.services.task_id_allocator import allocate_next_task_id
from application.users.services.teacher_activity_service import record_teacher_activity
from domain.entities.tasks.block_reorder_task import BlockReorderTask as BlockReorderTaskEntity
from shared.enums import AssignmentType, TaskType
from infrastructure.db.models.task import (
    BlockReorderTask as BlockReorderTaskModel,
    Task as TaskModel,
)


def create_block_reorder_task(
    db: Session,
    *,
    title: str,
    description: str,
    difficulty: str,
    original_code: str,
    template: str | None,
    language: str,
    language_variants: dict | None = None,
    teacher_id: int | None = None,
    constructions: list[str] | None = None,
    blocks: list[str] | None = None,
    correct_order: list[int] | None = None,
    assignment_type: str | None = None,
    test_cases: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    stored_type = assignment_type or AssignmentType.TASK_BUILD_FROM_BLOCKS.value
    parsed_difficulty = parse_difficulty(difficulty)
    if blocks is None or correct_order is None or not blocks or not correct_order:
        blocks, correct_order = build_shuffled_blocks(original_code)

    temp_entity = BlockReorderTaskEntity(
        id=0, teacher_id=teacher_id or 0, title=title, description=description,
        difficulty=parsed_difficulty, task_type=TaskType.BLOCK_REORDER,
        original_code=original_code, template=template, blocks=blocks,
        correct_order=correct_order, language=language,
        language_variants=language_variants, constructions=[],
    )
    canonical_code = build_canonical_code(temp_entity, language=language)
    default_test_cases = autogenerate_test_cases(language=language, canonical_code=canonical_code)
    stored_test_cases = test_cases if test_cases is not None else default_test_cases

    next_id = allocate_next_task_id(db)
    task_insert = db.execute(
        sa.insert(TaskModel.__table__).values(
            id=next_id, teacher_id=teacher_id, title=title, description=description,
            difficulty=str(difficulty), task_type=stored_type,
            test_cases=stored_test_cases, code_examples={}, flow_spec={},
        )
    )
    task_id = int(task_insert.inserted_primary_key[0] or next_id)
    db.execute(
        sa.insert(BlockReorderTaskModel.__table__).values(
            task_id=task_id, original_code=original_code, template=template,
            blocks=blocks, correct_order=correct_order, language=language,
            language_variants=language_variants,
        )
    )
    if teacher_id:
        record_teacher_activity(db, teacher_id, "created_task", commit=False)
    db.commit()

    entity = BlockReorderTaskEntity(
        id=task_id, teacher_id=teacher_id or 0, title=title, description=description,
        difficulty=parsed_difficulty, task_type=TaskType.BLOCK_REORDER,
        original_code=original_code, template=template, blocks=blocks,
        correct_order=correct_order, language=language,
        language_variants=language_variants, constructions=[],
    )
    payload = entity.to_public_payload()
    payload["task_id"] = task_id
    payload["id"] = task_id
    return payload
