from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from shared.interfaces.repositories.admin.teacher_role_request import (
    ITeacherRoleRequestRepository,
)
from domain.entities.users.teacher_role_request import TeacherRoleRequest
from shared.enums import TeacherRoleRequestStatus
from infrastructure.db.models.user.teacher_role_request import (
    TeacherRoleRequestModel,
)


class SqlAlchemyTeacherRoleRequestRepository(ITeacherRoleRequestRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, user_id: int, message: str | None = None) -> TeacherRoleRequest:
        model = TeacherRoleRequestModel(
            user_id=user_id,
            status=TeacherRoleRequestStatus.PENDING.value,
            message=message,
        )
        self._session.add(model)
        self._session.flush()
        self._session.refresh(model)
        return self._to_domain(model)

    def get_by_id(self, request_id: int) -> TeacherRoleRequest | None:
        model = self._session.get(TeacherRoleRequestModel, request_id)
        return self._to_domain(model) if model else None

    def get_pending_for_user(self, user_id: int) -> TeacherRoleRequest | None:
        stmt = (
            select(TeacherRoleRequestModel)
            .where(
                TeacherRoleRequestModel.user_id == user_id,
                TeacherRoleRequestModel.status == TeacherRoleRequestStatus.PENDING.value,
            )
            .order_by(TeacherRoleRequestModel.created_at.desc())
            .limit(1)
        )
        model = self._session.execute(stmt).scalar_one_or_none()
        return self._to_domain(model) if model else None

    def list_by_status(
        self, status: TeacherRoleRequestStatus | None = None
    ) -> list[TeacherRoleRequest]:
        stmt = (
            select(TeacherRoleRequestModel)
            .options(joinedload(TeacherRoleRequestModel.user))
            .order_by(TeacherRoleRequestModel.created_at.desc())
        )
        if status is not None:
            stmt = stmt.where(TeacherRoleRequestModel.status == status.value)
        models = self._session.execute(stmt).scalars().all()
        return [self._to_domain(m) for m in models]

    def update_status(
        self,
        request_id: int,
        status: TeacherRoleRequestStatus,
        reviewed_by_id: int,
    ) -> TeacherRoleRequest:
        model = self._session.get(TeacherRoleRequestModel, request_id)
        if model is None:
            raise ValueError("Teacher role request not found")
        model.status = status.value
        model.reviewed_by_id = reviewed_by_id
        model.reviewed_at = datetime.now(UTC)
        self._session.flush()
        self._session.refresh(model)
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: TeacherRoleRequestModel) -> TeacherRoleRequest:
        user = getattr(model, "user", None)
        return TeacherRoleRequest(
            id=model.id,
            user_id=model.user_id,
            status=TeacherRoleRequestStatus(model.status),
            created_at=model.created_at,
            reviewed_at=model.reviewed_at,
            reviewed_by_id=model.reviewed_by_id,
            message=model.message,
            user_name=user.name if user is not None else None,
            user_email=user.email if user is not None else None,
        )
