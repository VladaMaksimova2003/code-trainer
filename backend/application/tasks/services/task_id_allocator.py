"""Allocate monotonic task.id values (safe after seed scripts with explicit ids)."""
from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.orm import Session

from infrastructure.db.models.task import Task as TaskModel


def allocate_next_task_id(db: Session) -> int:
    return int(
        db.execute(
            sa.select(sa.func.coalesce(sa.func.max(TaskModel.__table__.c.id), 0) + 1)
        ).scalar_one()
    )
