"""Public / scoped user profile views for cross-user navigation."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from application.learning.skill_progress_service import build_skill_progress
from application.learning.use_cases.analytics.service import (
    _compute_level,
    _task_constructions,
    _teacher_group_student_ids,
)
from application.learning.use_cases.groups.dashboard import (
    _catalog_task_ids,
    _student_solved_in_catalog,
    build_student_group_task_progress,
)
from application.users.services.avatar_service import AvatarService
from application.users.services.teacher_service import (
    ensure_teacher_profile,
    get_teacher_user_or_404,
    is_teacher_user,
)
from application.auth.dto import CurrentUserResult
from domain.policies.rbac.rbac import has_role, normalize_role
from infrastructure.db.models.task.collection import Collection
from infrastructure.db.models.learning.group import Group, group_member_association_table
from infrastructure.db.models.learning.submission import Submission
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.models.user import User
from shared.enums import AssignmentSetVisibility, TaskVisibility, UserType


def _viewer_roles(viewer: CurrentUserResult) -> frozenset[UserType]:
    return frozenset(normalize_role(r) for r in viewer.roles)


def _is_admin(roles: frozenset[UserType]) -> bool:
    return has_role(roles, UserType.ADMIN)


def _student_in_teacher_groups(db: Session, student_id: int, teacher_id: int) -> bool:
    row = db.execute(
        select(group_member_association_table.c.group_id)
        .join(Group, Group.id == group_member_association_table.c.group_id)
        .where(
            group_member_association_table.c.student_id == student_id,
            Group.teacher_id == teacher_id,
        )
        .limit(1)
    ).first()
    return row is not None


def _groups_for_student_teacher(
    db: Session, student_id: int, teacher_id: int
) -> list[Group]:
    group_ids = list(
        db.execute(
            select(group_member_association_table.c.group_id)
            .join(Group, Group.id == group_member_association_table.c.group_id)
            .where(
                group_member_association_table.c.student_id == student_id,
                Group.teacher_id == teacher_id,
            )
        ).scalars().all()
    )
    if not group_ids:
        return []
    return db.query(Group).filter(Group.id.in_(group_ids)).order_by(Group.name).all()


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _teacher_active_task_ids(db: Session, teacher_id: int) -> set[int]:
    rows = db.execute(
        select(TaskModel.id).where(
            TaskModel.teacher_id == teacher_id,
            TaskModel.is_delete.is_(False),
        )
    ).scalars().all()
    return set(rows)


def _teacher_avg_pass_rate(db: Session, teacher_id: int) -> float:
    student_ids = _teacher_group_student_ids(db, teacher_id)
    task_ids = _teacher_active_task_ids(db, teacher_id)
    if not student_ids or not task_ids:
        return 0.0
    total, success = db.execute(
        select(
            func.count(Submission.id),
            func.count(Submission.id).filter(Submission.success.is_(True)),
        ).where(
            Submission.user_id.in_(student_ids),
            Submission.task_id.in_(task_ids),
        )
    ).one()
    total = int(total or 0)
    success = int(success or 0)
    return round(100.0 * success / total, 0) if total else 0.0


def _students_joined_last_week(db: Session, teacher_id: int) -> int:
    """Placeholder until group membership tracks join timestamps."""
    _ = db, teacher_id
    return 0


def _serialize_public_task(task: TaskModel) -> dict[str, Any]:
    raw = task.task_type
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description or "",
        "difficulty": task.difficulty,
        "task_type": raw,
        "type": raw if raw != "diagram" else "blocks",
    }


def _skills_for_student_tasks(
    db: Session, student_id: int, task_ids: set[int]
) -> list[dict[str, Any]]:
    if not task_ids:
        return []
    subs = (
        db.query(Submission)
        .filter(
            Submission.user_id == student_id,
            Submission.task_id.in_(task_ids),
        )
        .all()
    )
    task_attempts: dict[int, list[Submission]] = defaultdict(list)
    for s in subs:
        task_attempts[s.task_id].append(s)

    solved_ids = {
        tid for tid, lst in task_attempts.items() if any(x.success is True for x in lst)
    }

    def _constructions_for_task(task_id: int) -> list[str]:
        task = db.get(TaskModel, task_id)
        if task is None or task.is_delete:
            return []
        return _task_constructions(db, task)

    rows = build_skill_progress(
        accessible_task_ids=task_ids,
        solved_task_ids=solved_ids,
        get_constructions=_constructions_for_task,
    )
    return [
        {
            "id": row["id"],
            "label": row["label"],
            "percent": round(row["percent"]),
            "total": row["total"],
            "solved": row["solved"],
        }
        for row in rows
    ]


def _activity_by_date_for_tasks(
    db: Session, student_id: int, task_ids: set[int]
) -> dict[str, int]:
    if not task_ids:
        return {}
    from application.learning.activity_service import build_activity_by_date

    rows = (
        db.query(Submission)
        .filter(
            Submission.user_id == student_id,
            Submission.task_id.in_(task_ids),
        )
        .all()
    )
    return build_activity_by_date(rows)


def _streak_from_activity(by_date: dict[str, int]) -> int:
    today = _utc_now().date()
    cursor = today
    if not by_date.get(today.isoformat()):
        cursor = today - timedelta(days=1)
    streak = 0
    while by_date.get(cursor.isoformat(), 0) > 0:
        streak += 1
        cursor = cursor - timedelta(days=1)
    return streak


def can_view_teacher_profile(
    db: Session,
    viewer: CurrentUserResult,
    teacher_id: int,
) -> bool:
    roles = _viewer_roles(viewer)
    if _is_admin(roles) or viewer.id == teacher_id:
        return True
    profile = ensure_teacher_profile(db, get_teacher_user_or_404(db, teacher_id))
    if profile.is_public:
        return True
    if has_role(roles, UserType.STUDENT) and viewer.id in _teacher_group_student_ids(
        db, teacher_id
    ):
        return True
    return False


def can_view_student_teacher_profile(
    db: Session,
    viewer: CurrentUserResult,
    student_id: int,
    teacher_id: int,
) -> bool:
    roles = _viewer_roles(viewer)
    if _is_admin(roles):
        return True
    if viewer.id == teacher_id and _student_in_teacher_groups(db, student_id, teacher_id):
        return True
    if viewer.id == student_id and _student_in_teacher_groups(db, student_id, teacher_id):
        return True
    return False


def build_teacher_profile_view(
    db: Session,
    teacher_id: int,
    viewer: CurrentUserResult,
) -> dict[str, Any]:
    user = get_teacher_user_or_404(db, teacher_id)
    profile = ensure_teacher_profile(db, user)
    roles = _viewer_roles(viewer)
    is_owner = viewer.id == teacher_id
    is_admin = _is_admin(roles)

    if not can_view_teacher_profile(db, viewer, teacher_id):
        raise PermissionError("Profile is not available")

    total_tasks = db.scalar(
        select(func.count()).select_from(TaskModel).where(
            TaskModel.teacher_id == teacher_id,
            TaskModel.is_delete.is_(False),
        )
    ) or 0

    public_task_count = db.scalar(
        select(func.count()).select_from(TaskModel).where(
            TaskModel.teacher_id == teacher_id,
            TaskModel.is_delete.is_(False),
            TaskModel.visibility == TaskVisibility.PUBLIC,
        )
    ) or 0

    group_count = db.scalar(
        select(func.count()).select_from(Group).where(Group.teacher_id == teacher_id)
    ) or 0

    student_count = len(_teacher_group_student_ids(db, teacher_id))

    public_catalog_rows = (
        db.query(Collection)
        .filter(
            Collection.teacher_id == teacher_id,
            Collection.is_archived.is_(False),
            Collection.visibility == AssignmentSetVisibility.PUBLIC,
        )
        .order_by(Collection.name)
        .all()
    )

    public_catalogs: list[dict[str, Any]] = []
    for row in public_catalog_rows:
        task_ids = _catalog_task_ids(db, row.id)
        catalog_tasks: list[dict[str, Any]] = []
        for tid in task_ids:
            task_row = db.get(TaskModel, tid)
            if (
                task_row is None
                or task_row.is_delete
                or task_row.visibility != TaskVisibility.PUBLIC
            ):
                continue
            catalog_tasks.append(_serialize_public_task(task_row))
        public_catalogs.append(
            {
                "id": row.id,
                "title": row.name,
                "description": row.description or "",
                "task_count": len(catalog_tasks),
                "visibility": AssignmentSetVisibility.PUBLIC.value,
                "tasks": catalog_tasks,
            }
        )

    subtitle_parts = [p for p in [profile.specialization] if p]
    if profile.languages:
        subtitle_parts.append(", ".join(profile.languages[:3]))

    avg_pass_rate = _teacher_avg_pass_rate(db, teacher_id)
    students_week_delta = _students_joined_last_week(db, teacher_id)

    return {
        "kind": "teacher",
        "user_id": user.id,
        "display_name": profile.full_name or user.name,
        "full_name": profile.full_name or user.name,
        "email": user.email,
        "bio": profile.bio,
        "specialization": profile.specialization,
        "subtitle": " · ".join(subtitle_parts) if subtitle_parts else None,
        "languages": profile.languages or [],
        "avatar": AvatarService.to_dict(
            user.id, profile.full_name or user.name, role="teacher"
        ),
        "role_label": "teacher",
        "is_public": bool(profile.is_public),
        "is_own_profile": is_owner,
        "can_browse_catalogs": len(public_catalogs) > 0,
        "stats": {
            "total_tasks": int(total_tasks),
            "public_tasks": int(public_task_count),
            "active_tasks": int(total_tasks),
            "groups": int(group_count),
            "students": int(student_count),
            "students_week_delta": students_week_delta,
            "public_catalogs": len(public_catalogs),
            "avg_pass_rate": avg_pass_rate,
        },
        "public_catalogs": public_catalogs,
    }


def _last_activity_on_tasks(
    db: Session, student_id: int, task_ids: list[int]
) -> str | None:
    if not task_ids:
        return None
    last_sub = (
        db.query(Submission)
        .filter(
            Submission.user_id == student_id,
            Submission.task_id.in_(task_ids),
        )
        .order_by(Submission.created_at.desc())
        .first()
    )
    if last_sub and last_sub.created_at:
        return last_sub.created_at.isoformat()
    return None


def build_student_teacher_profile_view(
    db: Session,
    student_id: int,
    teacher_id: int,
    viewer: CurrentUserResult,
) -> dict[str, Any]:
    get_teacher_user_or_404(db, teacher_id)
    student = db.get(User, student_id)
    if student is None:
        raise ValueError("Student not found")

    if not can_view_student_teacher_profile(db, viewer, student_id, teacher_id):
        raise PermissionError("Profile is not available")

    groups = _groups_for_student_teacher(db, student_id, teacher_id)
    teacher = db.get(User, teacher_id)

    task_union: set[int] = set()
    catalogs_out: list[dict[str, Any]] = []

    for group in groups:
        progress = build_student_group_task_progress(
            db, teacher_id, group.id, student_id
        )
        if progress is None:
            continue
        for catalog in progress["catalogs"]:
            catalogs_out.append({**catalog, "group_id": group.id, "group_name": group.name})
            for task in catalog.get("tasks", []):
                task_union.add(task["task_id"])

    total_tasks = len(task_union)
    solved_count = len(_student_solved_in_catalog(db, student_id, list(task_union)))
    progress_percent = round(100.0 * solved_count / total_tasks, 1) if total_tasks else 0.0

    total_submissions = 0
    successful_submissions = 0
    if task_union:
        total_submissions, successful_submissions = db.execute(
            select(
                func.count(Submission.id),
                func.count(Submission.id).filter(Submission.success.is_(True)),
            ).where(
                Submission.user_id == student_id,
                Submission.task_id.in_(task_union),
            )
        ).one()
        total_submissions = int(total_submissions or 0)
        successful_submissions = int(successful_submissions or 0)

    success_rate = (
        round(100.0 * successful_submissions / total_submissions, 1)
        if total_submissions
        else 0.0
    )

    activity_by_date = _activity_by_date_for_tasks(db, student_id, task_union)
    streak_days = _streak_from_activity(activity_by_date)
    level = _compute_level(solved_count / total_tasks if total_tasks else 0.0)
    skills = _skills_for_student_tasks(db, student_id, task_union)
    handle = None
    if student.email:
        handle = f"@{student.email.split('@')[0]}"

    primary_group = groups[0].name if groups else None

    return {
        "kind": "student",
        "user_id": student.id,
        "display_name": student.name,
        "about": student.about,
        "handle": handle,
        "avatar": AvatarService.to_dict(student.id, student.name, role="student"),
        "role_label": "student",
        "level": level,
        "teacher": {
            "id": teacher_id,
            "name": teacher.name if teacher else f"Преподаватель #{teacher_id}",
        },
        "groups": [{"id": g.id, "name": g.name} for g in groups],
        "primary_group": primary_group,
        "summary": {
            "solved_count": solved_count,
            "total_tasks": total_tasks,
            "progress_percent": progress_percent,
            "total_submissions": total_submissions,
            "successful_submissions": successful_submissions,
            "success_rate": success_rate,
            "streak_days": streak_days,
            "last_activity_at": _last_activity_on_tasks(db, student_id, list(task_union)),
        },
        "skills": skills,
        "catalogs": catalogs_out,
        "is_own_profile": viewer.id == student_id,
    }

