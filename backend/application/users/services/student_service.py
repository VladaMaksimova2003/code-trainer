"""Aggregated data for the student LMS-style profile dashboard."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from application.learning.activity_service import build_activity_by_date
from application.tasks.services.catalog.task_display import display_title_for_task_model
from application.users.services.avatar_service import AvatarService
from application.users.services.study_identity import get_study_identity
from application.auth.dto import CurrentUserResult
from domain.policies.rbac.rbac import has_any_role, normalize_role, primary_role
from shared.enums import UserType
from infrastructure.db.models.learning.submission import Submission
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.models.user import User

_DEFAULT_TS = datetime(1970, 1, 1, tzinfo=timezone.utc)


def _streak_from_activity(activity_by_date: dict[str, int]) -> int:
    if not activity_by_date:
        return 0
    cursor = datetime.now(timezone.utc).date()
    if not activity_by_date.get(cursor.isoformat()):
        cursor = cursor - timedelta(days=1)
    streak = 0
    while activity_by_date.get(cursor.isoformat(), 0) > 0:
        streak += 1
        cursor = cursor - timedelta(days=1)
    return streak


def ensure_student(user: CurrentUserResult, db: Session) -> User:
    row = db.query(User).filter(User.id == user.id).first()
    if row is None:
        raise ValueError("Student not found")
    roles = frozenset(normalize_role(r) for r in user.roles)
    if not has_any_role(roles, UserType.STUDENT, UserType.TEACHER, UserType.ADMIN):
        raise ValueError("Student not found")
    return row


def build_student_profile(
    db: Session,
    viewer: CurrentUserResult,
) -> dict[str, Any]:
    user_row = ensure_student(viewer, db)
    uid = user_row.id

    subs = (
        db.query(Submission)
        .filter(Submission.user_id == uid)
        .order_by(Submission.created_at.desc())
        .all()
    )

    total_submissions = len(subs)
    successful = sum(1 for s in subs if s.success is True)
    failed_or_pending = total_submissions - successful

    task_attempts: dict[int, list[Submission]] = {}
    for s in subs:
        task_attempts.setdefault(s.task_id, []).append(s)

    solved_task_ids = {
        tid for tid, lst in task_attempts.items() if any(x.success is True for x in lst)
    }
    solved_tasks_count = len(solved_task_ids)
    attempted_tasks_count = len(task_attempts)

    success_rate = round(100.0 * successful / total_submissions, 1) if total_submissions else 0.0

    activity_by_date = build_activity_by_date(subs)
    streak_days = _streak_from_activity(activity_by_date)

    task_ids = list({s.task_id for s in subs})
    task_models: dict[int, TaskModel] = {}
    if task_ids:
        task_models = {
            r.id: r
            for r in db.query(TaskModel).filter(TaskModel.id.in_(task_ids)).all()
        }

    recent_submissions = [
        _serialize_submission_preview(
            s,
            task_title=display_title_for_task_model(task_models[s.task_id])
            if s.task_id in task_models
            else None,
        )
        for s in subs
    ]

    role = primary_role(frozenset(normalize_role(r) for r in viewer.roles))
    study = get_study_identity(db, uid)

    return {
        "user_id": uid,
        "display_name": user_row.name,
        "email": user_row.email,
        "about": user_row.about,
        "study_place": study["study_place"],
        "study_group": study["study_group"],
        "study_identity": study["study_identity"],
        "role": role.value.title(),
        "role_label": role.value,
        "avatar": AvatarService.to_dict(user_row.id, user_row.name, role="student"),
        "solved_tasks_count": solved_tasks_count,
        "attempted_tasks_count": attempted_tasks_count,
        "total_submissions": total_submissions,
        "successful_submissions": successful,
        "failed_or_pending_submissions": failed_or_pending,
        "success_rate": success_rate,
        "activity_by_date": activity_by_date,
        "streak_days": streak_days,
        "recent_submissions": recent_submissions,
        "progress": {
            "solved_tasks_count": solved_tasks_count,
            "attempted_tasks_count": attempted_tasks_count,
            "total_submissions": total_submissions,
            "success_rate": success_rate,
        },
    }


def _serialize_submission_preview(
    submission: Submission,
    *,
    task_title: str | None = None,
) -> dict[str, Any]:
    return {
        "id": submission.id,
        "task_id": submission.task_id,
        "task_title": task_title or f"Задача #{submission.task_id}",
        "language": submission.language,
        "status": submission.status,
        "success": submission.success,
        "created_at": submission.created_at.isoformat() if submission.created_at else None,
    }
