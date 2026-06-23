from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from shared.interfaces.repositories.learning.teacher_search import (
    ITeacherSearchRepository,
    TeacherSearchFilters,
    TeacherSearchResult,
)
from shared.enums import AssignmentWorkflowStatus, UserType
from infrastructure.db.models.task.collection import Collection
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.models.user.teacher_profile import TeacherProfile
from infrastructure.db.models.user import User
from infrastructure.db.models.user.user_role import UserRole as UserRoleModel


class SqlAlchemyTeacherSearchRepository(ITeacherSearchRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def _base_query(self):
        return (
            select(
                User.id,
                TeacherProfile.full_name,
                TeacherProfile.bio,
                TeacherProfile.languages,
                TeacherProfile.specialization,
                func.count(func.distinct(TaskModel.id)).label("assignment_count"),
                func.count(func.distinct(Collection.id)).label("set_count"),
            )
            .join(TeacherProfile, TeacherProfile.user_id == User.id)
            .join(UserRoleModel, UserRoleModel.user_id == User.id)
            .outerjoin(
                TaskModel,
                (TaskModel.teacher_id == User.id)
                & (TaskModel.is_delete.is_(False))
                & (TaskModel.workflow_status == AssignmentWorkflowStatus.ACTIVE.value),
            )
            .outerjoin(
                Collection,
                (Collection.teacher_id == User.id) & (Collection.is_archived.is_(False)),
            )
            .where(
                UserRoleModel.role == UserType.TEACHER.value,
                User.is_deleted.is_(False),
                User.is_blocked.is_(False),
                TeacherProfile.is_public.is_(True),
            )
            .group_by(
                User.id,
                TeacherProfile.full_name,
                TeacherProfile.bio,
                TeacherProfile.languages,
                TeacherProfile.specialization,
            )
        )

    def _apply_filters(self, stmt, filters: TeacherSearchFilters):
        if filters.name:
            pattern = f"%{filters.name.strip()}%"
            stmt = stmt.where(
                or_(
                    TeacherProfile.full_name.ilike(pattern),
                    User.name.ilike(pattern),
                    User.email.ilike(pattern),
                )
            )
        if filters.language:
            lang = filters.language.strip().lower()
            stmt = stmt.where(TeacherProfile.languages.contains([lang]))
        if filters.specialization:
            stmt = stmt.where(
                TeacherProfile.specialization.ilike(f"%{filters.specialization.strip()}%")
            )
        return stmt

    def search(self, filters: TeacherSearchFilters, limit: int = 50) -> list[TeacherSearchResult]:
        stmt = self._apply_filters(self._base_query(), filters).limit(limit)
        return [self._row_to_result(row) for row in self._session.execute(stmt).all()]

    def get_public_profile(self, teacher_id: int) -> TeacherSearchResult | None:
        stmt = self._base_query().where(
            User.id == teacher_id,
            TeacherProfile.is_public.is_(True),
        )
        row = self._session.execute(stmt).first()
        return self._row_to_result(row) if row else None

    @staticmethod
    def _row_to_result(row) -> TeacherSearchResult:
        return TeacherSearchResult(
            user_id=row.id,
            full_name=row.full_name or "",
            bio=row.bio,
            languages=row.languages or [],
            specialization=row.specialization,
            assignment_count=int(row.assignment_count or 0),
            assignment_set_count=int(row.set_count or 0),
        )
