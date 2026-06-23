from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from shared.interfaces.repositories.admin.admin_user import (
    AdminUserDetail,
    AdminUserListItem,
    IAdminUserRepository,
)
from shared.enums import UserType
from infrastructure.db.models.learning.submission import Submission
from infrastructure.db.models.task.collection import Collection
from infrastructure.db.models.learning.group import Group
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.models.user import User as UserModel
from infrastructure.db.models.user.auth_session import AuthSession as AuthSessionModel
from infrastructure.repositories.users.user_role import SqlAlchemyUserRoleRepository


class SqlAlchemyAdminUserRepository(IAdminUserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session
        self._roles = SqlAlchemyUserRoleRepository(session)

    def list_users(self, include_deleted: bool = False) -> list[AdminUserListItem]:
        stmt = select(UserModel).order_by(UserModel.id.asc())
        if not include_deleted:
            stmt = stmt.where(UserModel.is_deleted.is_(False))
        users = self._session.execute(stmt).scalars().all()
        return [self._to_list_item(u) for u in users]

    def get_user_detail(self, user_id: int) -> AdminUserDetail | None:
        user = self._session.get(UserModel, user_id)
        if user is None:
            return None
        base = self._to_list_item(user)
        subs = (
            self._session.query(Submission)
            .filter(Submission.user_id == user_id)
            .all()
        )
        successful = sum(1 for s in subs if s.success is True)
        solved_tasks = len({s.task_id for s in subs if s.success is True})
        success_rate = round(100.0 * successful / len(subs), 1) if subs else 0.0

        from application.learning.activity_service import build_activity_by_date

        activity_by_date = build_activity_by_date(subs)
        streak_days = _compute_streak_days(activity_by_date)

        member_groups = list(user.groups or [])
        member_group_names = [g.name for g in member_groups if getattr(g, "name", None)]

        last_login_at = self._session.scalar(
            select(func.max(AuthSessionModel.created_at)).where(
                AuthSessionModel.user_id == user_id,
                AuthSessionModel.revoked_at.is_(None),
            )
        )

        roles = base.roles
        is_teacher = UserType.TEACHER.value in roles or UserType.ADMIN.value in roles
        created_tasks_count = None
        created_catalogs_count = None
        groups_count = None
        if is_teacher:
            created_tasks_count = int(
                self._session.scalar(
                    select(func.count())
                    .select_from(TaskModel)
                    .where(TaskModel.teacher_id == user_id, TaskModel.is_delete.is_(False))
                )
                or 0
            )
            created_catalogs_count = int(
                self._session.scalar(
                    select(func.count()).select_from(Collection).where(Collection.teacher_id == user_id)
                )
                or 0
            )
            groups_count = int(
                self._session.scalar(
                    select(func.count()).select_from(Group).where(Group.teacher_id == user_id)
                )
                or 0
            )

        return AdminUserDetail(
            id=base.id,
            name=base.name,
            email=base.email,
            roles=base.roles,
            is_blocked=base.is_blocked,
            is_deleted=base.is_deleted,
            created_at=base.created_at,
            total_submissions=len(subs),
            successful_submissions=successful,
            solved_tasks_count=solved_tasks,
            last_login_at=last_login_at,
            created_tasks_count=created_tasks_count,
            created_catalogs_count=created_catalogs_count,
            groups_count=groups_count,
            about=user.about,
            success_rate=success_rate,
            streak_days=streak_days,
            member_groups_count=len(member_groups),
            member_group_names=member_group_names,
        )

    def set_blocked(self, user_id: int, blocked: bool) -> None:
        user = self._session.get(UserModel, user_id)
        if user is None:
            raise ValueError("User not found")
        user.is_blocked = blocked
        self._session.flush()

    def soft_delete(self, user_id: int) -> None:
        from shared.enums import AssignmentWorkflowStatus

        user = self._session.get(UserModel, user_id)
        if user is None:
            raise ValueError("User not found")
        user.is_deleted = True
        user.is_blocked = True
        for task in (
            self._session.execute(select(TaskModel).where(TaskModel.teacher_id == user_id))
            .scalars()
            .all()
        ):
            task.workflow_status = AssignmentWorkflowStatus.ARCHIVED.value
        self._session.flush()

    def _to_list_item(self, model: UserModel) -> AdminUserListItem:
        roles = self._roles.get_roles_for_user(model.id)
        return AdminUserListItem(
            id=model.id,
            name=model.name,
            email=model.email,
            roles=sorted(r.value for r in roles),
            is_blocked=bool(model.is_blocked),
            is_deleted=bool(model.is_deleted),
            created_at=model.created_at,
        )


def _compute_streak_days(activity_by_date: dict[str, int]) -> int:
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
