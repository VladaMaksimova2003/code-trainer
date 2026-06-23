"""Progress counters for student assignment sets."""

from __future__ import annotations

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from infrastructure.db.models.learning.submission import Submission
from infrastructure.db.models.task.task import Task as TaskModel


def active_task_ids(session: Session, task_ids: list[int]) -> list[int]:
    if not task_ids:
        return []
    rows = session.execute(
        select(TaskModel.id).where(
            TaskModel.id.in_(task_ids),
            TaskModel.is_delete.is_(False),
        )
    ).scalars().all()
    return [int(task_id) for task_id in rows]


def assignment_set_progress(
    session: Session,
    *,
    user_id: int | None,
    task_ids: list[int],
) -> tuple[int, int]:
    active_ids = active_task_ids(session, task_ids)
    total = len(active_ids)
    if not user_id or not active_ids:
        return total, 0
    solved = int(
        session.scalar(
            select(func.count(distinct(Submission.task_id))).where(
                Submission.user_id == user_id,
                Submission.task_id.in_(active_ids),
                Submission.success.is_(True),
            )
        )
        or 0
    )
    return total, solved
