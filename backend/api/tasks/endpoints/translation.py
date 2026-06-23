"""Translation task endpoints (teacher authoring: read & update)."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.dependencies.authorization import require_permission
from application.auth.dto import CurrentUserResult
from application.tasks.use_cases.translation.task import (
    get_translation_authoring_payload,
    update_translation_task,
)
from domain.policies.permissions.permissions import Permission
from domain.policies.rbac.role import normalized_role_key
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.session import get_db

router = APIRouter(prefix="/translation")


class TranslationUpdateRequest(BaseModel):
    title: str
    description: str
    difficulty: str = "easy"
    source_code: str = ""
    source_language: str = "python"
    language_codes: dict[str, str] | None = None
    test_cases: list[dict[str, Any]] = Field(default_factory=list)
    patterns: list[str] | None = None
    patterns_by_language: dict[str, list[str]] | None = None
    task_type: str | None = None
    is_debug_task: bool | None = None


def _ensure_can_edit(task_row: TaskModel, current_user: CurrentUserResult) -> None:
    roles = frozenset(normalized_role_key(r) for r in current_user.roles)
    if "TEACHER" in roles and "ADMIN" not in roles:
        if task_row.teacher_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only edit your own tasks.",
            )


@router.get("/{task_id}/author")
async def get_translation_author(
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

    payload = get_translation_authoring_payload(db, task_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Translation task not found")
    return payload


@router.put("/{task_id}")
async def update_translation(
    task_id: int,
    request: TranslationUpdateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.EDIT_ASSIGNMENTS)
    ),
):
    task_row = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task_row or task_row.is_delete:
        raise HTTPException(status_code=404, detail="Translation task not found")
    _ensure_can_edit(task_row, current_user)

    updated = update_translation_task(
        db,
        task_id,
        title=request.title,
        description=request.description,
        difficulty=request.difficulty,
        source_code=request.source_code,
        source_language=request.source_language,
        language_codes=request.language_codes,
        test_cases=request.test_cases,
        patterns=request.patterns,
        patterns_by_language=request.patterns_by_language,
        task_type=request.task_type,
        is_debug_task=request.is_debug_task,
        teacher_id=current_user.id,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Translation task not found")
    return updated
