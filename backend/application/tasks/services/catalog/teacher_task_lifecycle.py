"""Teacher task retire (delete vs archive) and custom chapter removal."""

from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from shared.enums import AssignmentWorkflowStatus
from shared.exceptions import AccessDeniedToContentError, TaskNotFoundError
from infrastructure.db.models.learning.submission import Submission
from infrastructure.db.models.task import Task as TaskModel


@dataclass(frozen=True)
class TaskRetireResult:
    action: str
    task_id: int
    submissions_count: int


def count_task_submissions(session: Session, task_id: int) -> int:
    return int(
        session.scalar(
            select(func.count()).select_from(Submission).where(Submission.task_id == task_id)
        )
        or 0
    )


def _ensure_teacher_can_edit_task(
    task: TaskModel,
    *,
    teacher_id: int,
    is_admin: bool,
) -> None:
    if is_admin:
        return
    if task.teacher_id != teacher_id:
        raise AccessDeniedToContentError("You can only modify your own tasks.")


def retire_task(
    session: Session,
    *,
    task_id: int,
    teacher_id: int,
    is_admin: bool = False,
) -> TaskRetireResult:
    """Soft-delete when no submissions; archive when students already attempted the task."""
    task = session.get(TaskModel, task_id)
    if task is None or task.is_delete:
        raise TaskNotFoundError(f"Task {task_id} not found")

    _ensure_teacher_can_edit_task(task, teacher_id=teacher_id, is_admin=is_admin)

    submissions_count = count_task_submissions(session, task_id)
    if submissions_count > 0:
        task.workflow_status = AssignmentWorkflowStatus.ARCHIVED.value
        session.flush()
        return TaskRetireResult(
            action="archived",
            task_id=task_id,
            submissions_count=submissions_count,
        )

    from infrastructure.repositories.tasks.task_catalog import SqlAlchemyCatalogTaskRelationRepository

    SqlAlchemyCatalogTaskRelationRepository(session).remove_all_for_task(task_id)
    task.is_delete = True
    session.flush()
    return TaskRetireResult(
        action="deleted",
        task_id=task_id,
        submissions_count=0,
    )


def set_teacher_task_workflow_status(
    session: Session,
    *,
    task_id: int,
    teacher_id: int,
    status: AssignmentWorkflowStatus,
    is_admin: bool = False,
) -> None:
    task = session.get(TaskModel, task_id)
    if task is None or task.is_delete:
        raise TaskNotFoundError(f"Task {task_id} not found")

    _ensure_teacher_can_edit_task(task, teacher_id=teacher_id, is_admin=is_admin)

    if status not in {
        AssignmentWorkflowStatus.ACTIVE,
        AssignmentWorkflowStatus.ARCHIVED,
    }:
        raise ValueError(f"unsupported workflow status: {status.value}")

    task.workflow_status = status.value
    session.flush()
