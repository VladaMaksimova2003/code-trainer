"""Append-only teacher activity rows for LMS-style heatmaps."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from infrastructure.db.models.user.teacher_activity import TeacherActivity


def record_teacher_activity(
    db: Session,
    teacher_id: int | None,
    action_type: str,
    *,
    commit: bool = True,
) -> None:
    if not teacher_id:
        return
    row = TeacherActivity(
        teacher_id=teacher_id,
        action_type=action_type,
        occurred_at=datetime.now(timezone.utc),
    )
    db.add(row)
    if commit:
        db.commit()
