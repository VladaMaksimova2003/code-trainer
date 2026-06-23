"""Use case: validate block-reorder / code-assembly solution (async execution)."""
from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from application.execution.block_reorder_validation import (
    enqueue_block_reorder_execution,
    validate_block_reorder_structural,
)


def validate_block_reorder_solution(
    db: Session,
    task_id: int,
    order: list[int],
    language: str | None = None,
    indents: list[int] | None = None,
    assembled_code: str | None = None,
    *,
    user_id: str = "anonymous",
) -> dict[str, Any] | None:
    structural = validate_block_reorder_structural(
        db,
        task_id,
        order,
        language=language,
        indents=indents,
        assembled_code=assembled_code,
    )
    if structural is None:
        return None
    return enqueue_block_reorder_execution(structural, user_id=user_id)
