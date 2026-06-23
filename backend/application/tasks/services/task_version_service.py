"""Persist assignment version snapshots after teacher/admin edits."""

from __future__ import annotations

from sqlalchemy.orm import Session

from infrastructure.repositories.tasks.admin_task import SqlAlchemyAdminTaskRepository


def record_task_version_after_edit(session: Session, task_id: int) -> int:
    """Bump task.version and store a snapshot of the current assignment state."""
    repo = SqlAlchemyAdminTaskRepository(session)
    item = repo.create_version_snapshot(task_id)
    return int(item.version_number)
