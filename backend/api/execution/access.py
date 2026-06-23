from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from application.auth.dto import CurrentUserResult
from application.tasks.services.content_access_service import ContentAccessService
from domain.policies.rbac.rbac import normalize_role
from infrastructure.db.models.task import Task as TaskModel
from shared.enums import UserType
from shared.exceptions import AccessDeniedToContentError


def normalized_roles(current_user: CurrentUserResult) -> frozenset[UserType]:
    return frozenset(normalize_role(role) for role in current_user.roles)


def ensure_task_access(
    db: Session,
    current_user: CurrentUserResult,
    task_id: int,
) -> None:
    access = ContentAccessService(db)
    try:
        access.ensure_task_access(current_user.id, normalized_roles(current_user), task_id)
    except AccessDeniedToContentError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc


def ensure_submission_access(
    db: Session,
    current_user: CurrentUserResult,
    submission_user_id: int | None,
    task_id: int,
) -> None:
    roles = normalized_roles(current_user)
    if submission_user_id == current_user.id or UserType.ADMIN in roles:
        return
    if UserType.TEACHER in roles:
        task = db.get(TaskModel, task_id)
        if task is not None and task.teacher_id == current_user.id:
            return
    raise HTTPException(status_code=403, detail="You do not have access to this submission.")


def ensure_job_access(current_user: CurrentUserResult, job_user_id: str) -> None:
    roles = normalized_roles(current_user)
    if UserType.ADMIN in roles or job_user_id == str(current_user.id):
        return
    raise HTTPException(status_code=403, detail="You do not have access to this job.")
