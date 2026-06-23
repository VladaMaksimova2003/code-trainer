"""Guest demo access helpers."""
from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from application.tasks.services.content_access_service import ContentAccessService


def ensure_public_task(db: Session, task_id: int) -> None:
    access = ContentAccessService(db)
    if not access.is_public_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
