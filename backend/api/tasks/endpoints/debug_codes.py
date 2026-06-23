"""Teacher endpoints for debug-task reference code (fixed vs buggy)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.dependencies.authorization import require_permission
from application.auth.dto import CurrentUserResult
from application.tasks.use_cases.debug_codes import (
    get_debug_codes_authoring,
    update_debug_codes,
)
from domain.policies.permissions.permissions import Permission
from domain.policies.rbac.role import normalized_role_key
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.session import get_db

router = APIRouter(prefix="/debug-codes")


class DebugCodesUpdateRequest(BaseModel):
    fixed_codes: dict[str, str] | None = None
    buggy_codes: dict[str, str] | None = None


def _ensure_can_edit(task_row: TaskModel, current_user: CurrentUserResult) -> None:
    roles = frozenset(normalized_role_key(r) for r in current_user.roles)
    if "TEACHER" in roles and "ADMIN" not in roles:
        if task_row.teacher_id != current_user.id:
            raise HTTPException(status_code=403, detail="You can only edit your own tasks.")


@router.get("/{task_id}")
async def get_debug_codes(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.EDIT_ASSIGNMENTS)
    ),
):
    task_row = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task_row or task_row.is_delete:
        raise HTTPException(status_code=404, detail="Task not found")
    _ensure_can_edit(task_row, current_user)

    payload = get_debug_codes_authoring(db, task_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Debug task not found")
    return payload


@router.put("/{task_id}")
async def put_debug_codes(
    task_id: int,
    request: DebugCodesUpdateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.EDIT_ASSIGNMENTS)
    ),
):
    task_row = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task_row or task_row.is_delete:
        raise HTTPException(status_code=404, detail="Task not found")
    _ensure_can_edit(task_row, current_user)

    payload = update_debug_codes(
        db,
        task_id,
        fixed_codes=request.fixed_codes,
        buggy_codes=request.buggy_codes,
    )
    if payload is None:
        raise HTTPException(status_code=404, detail="Debug task not found")
    return payload
