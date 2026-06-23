"""Flowchart task endpoints (teacher authoring: read & update)."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from api.dependencies.authorization import require_permission
from application.auth.dto import CurrentUserResult
from application.tasks.use_cases.flowchart.task import (
    get_flowchart_authoring_payload,
    update_flowchart_task,
)
from domain.policies.permissions.permissions import Permission
from domain.policies.rbac.role import normalized_role_key
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.session import get_db

router = APIRouter(prefix="/flowchart")


class FlowchartUpdateRequest(BaseModel):
    title: str
    description: str
    difficulty: str = "easy"
    diagram: dict[str, Any] = Field(default_factory=dict)
    flow_spec: dict[str, Any] | None = None
    reference_code: str = ""
    expose_reference_code: bool = False
    language: str = "python"
    test_cases: list[dict[str, Any]] = Field(default_factory=list)
    patterns: list[str] | None = None
    task_type: str | None = None


def _ensure_can_edit(task_row: TaskModel, current_user: CurrentUserResult) -> None:
    roles = frozenset(normalized_role_key(r) for r in current_user.roles)
    if "TEACHER" in roles and "ADMIN" not in roles:
        if task_row.teacher_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="You can only edit your own tasks.",
            )


@router.get("/{task_id}/author")
async def get_flowchart_author(
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

    payload = get_flowchart_authoring_payload(db, task_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Flowchart task not found")
    return payload


@router.put("/{task_id}")
async def update_flowchart(
    task_id: int,
    request: FlowchartUpdateRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUserResult = Depends(
        require_permission(Permission.EDIT_ASSIGNMENTS)
    ),
):
    task_row = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task_row or task_row.is_delete:
        raise HTTPException(status_code=404, detail="Flowchart task not found")
    _ensure_can_edit(task_row, current_user)

    try:
        updated = update_flowchart_task(
            db,
            task_id,
            title=request.title,
            description=request.description,
            difficulty=request.difficulty,
            diagram=request.diagram,
            flow_spec=request.flow_spec,
            reference_code=request.reference_code,
            expose_reference_code=request.expose_reference_code,
            language=request.language,
            test_cases=request.test_cases,
            patterns=request.patterns,
            task_type=request.task_type,
            teacher_id=current_user.id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if not updated:
        raise HTTPException(status_code=404, detail="Flowchart task not found")
    return updated
