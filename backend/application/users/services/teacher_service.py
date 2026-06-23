"""Teacher profile aggregation and lookups."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from application.users.services.avatar_service import AvatarService
from application.auth.dto import CurrentUserResult
from domain.policies.permissions.permissions import Permission, can
from domain.policies.rbac.rbac import has_role, normalize_role
from domain.policies.rbac.role import Role, normalized_role_key
from shared.enums import UserType
from infrastructure.repositories.users.user_role import SqlAlchemyUserRoleRepository
from infrastructure.db.models.task.collection import Collection
from infrastructure.db.models.learning.group import Group
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.models.user.teacher_activity import TeacherActivity
from infrastructure.db.models.user.teacher_profile import TeacherProfile
from infrastructure.db.models.user import User


def ensure_teacher_profile(db: Session, user: User) -> TeacherProfile:
    profile = db.query(TeacherProfile).filter(TeacherProfile.user_id == user.id).first()
    if profile is None:
        profile = TeacherProfile(
            user_id=user.id,
            full_name=user.name or "",
            bio=None,
            languages=[],
            avatar_url=None,
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile


def is_teacher_user(db: Session, user: User) -> bool:
    roles = SqlAlchemyUserRoleRepository(db).get_roles_for_user(user.id)
    return UserType.TEACHER in roles or UserType.ADMIN in roles


def can_edit_teacher_dashboard(viewer: CurrentUserResult, teacher_user_id: int) -> bool:
    viewer_roles = frozenset(normalize_role(r) for r in viewer.roles)
    if has_role(viewer_roles, UserType.ADMIN):
        return True
    return (
        has_role(viewer_roles, UserType.TEACHER)
        and viewer.id == teacher_user_id
    )


def get_teacher_user_or_404(db: Session, teacher_id: int) -> User:
    user = db.query(User).filter(User.id == teacher_id).first()
    if user is None or not is_teacher_user(db, user):
        raise ValueError("Teacher not found")
    return user


def _public_task_type(raw: str) -> str:
    if raw == "diagram":
        return "blocks"
    return raw


def build_profile_bundle(
    db: Session,
    teacher_id: int,
    viewer: CurrentUserResult | None,
) -> dict[str, Any]:
    user = get_teacher_user_or_404(db, teacher_id)
    profile = ensure_teacher_profile(db, user)

    total_tasks = db.scalar(
        select(func.count()).select_from(TaskModel).where(
            TaskModel.teacher_id == teacher_id,
            TaskModel.is_delete == False,
        )
    ) or 0

    groups = (
        db.query(Group.id, Group.name)
        .filter(Group.teacher_id == teacher_id)
        .order_by(Group.name)
        .all()
    )

    cols = (
        db.query(Collection.id, Collection.name)
        .filter(Collection.teacher_id == teacher_id)
        .order_by(Collection.name)
        .all()
    )

    can_edit_tasks = False
    can_manage_groups = False
    can_manage_catalogs = False
    if viewer is not None:
        viewer_roles = frozenset(normalize_role(r) for r in viewer.roles)
        can_edit_tasks = can_edit_teacher_dashboard(viewer, teacher_id)
        can_manage_groups = can(viewer_roles, Permission.MANAGE_GROUPS)
        can_manage_catalogs = can(viewer_roles, Permission.MANAGE_ASSIGNMENT_SETS)

    role_label = Role.TEACHER.value

    return {
        "user_id": user.id,
        "email": user.email,
        "display_name": user.name,
        "full_name": profile.full_name or user.name,
        "bio": profile.bio,
        "avatar": AvatarService.to_dict(
            user.id, profile.full_name or user.name, role="teacher"
        ),
        "languages": profile.languages or [],
        "specialization": profile.specialization,
        "role_label": role_label,
        "role": "Teacher",
        "total_tasks": int(total_tasks),
        "groups": [{"id": g.id, "name": g.name} for g in groups],
        "collections": [{"id": c.id, "name": c.name} for c in cols],
        "permissions": {
            "edit_tasks": can_edit_tasks,
            "manage_groups": can_manage_groups,
            "manage_catalogs": can_manage_catalogs,
        },
    }


def list_teacher_tasks(
    db: Session,
    teacher_id: int,
) -> list[dict[str, Any]]:
    get_teacher_user_or_404(db, teacher_id)

    stmt = (
        select(TaskModel)
        .where(
            TaskModel.teacher_id == teacher_id,
            TaskModel.is_delete == False,
        )
        .order_by(TaskModel.id)
    )

    rows = db.execute(stmt).scalars().all()
    out: list[dict[str, Any]] = []
    for t in rows:
        raw = t.task_type
        public = _public_task_type(raw)
        out.append(
            {
                "id": t.id,
                "title": t.title,
                "description": t.description,
                "difficulty": t.difficulty,
                "task_type": raw,
                "type": public,
                "editable_block_task": raw
                in {"block_reorder", "code_assembly", "task_build_from_blocks"},
            }
        )
    return out


def build_activity_payload(
    db: Session,
    teacher_id: int,
    days: int = 371,
) -> dict[str, Any]:
    get_teacher_user_or_404(db, teacher_id)
    start_dt = datetime.now(timezone.utc) - timedelta(days=days)
    rows = db.scalars(
        select(TeacherActivity)
        .where(
            TeacherActivity.teacher_id == teacher_id,
            TeacherActivity.occurred_at >= start_dt,
        )
        .order_by(TeacherActivity.occurred_at)
    ).all()
    by_date: dict[str, int] = {}
    for row in rows:
        key = row.occurred_at.astimezone(timezone.utc).date().isoformat()
        by_date[key] = by_date.get(key, 0) + 1
    return {
        "teacher_id": teacher_id,
        "days": days,
        "by_date": by_date,
        "total_events": len(rows),
    }
