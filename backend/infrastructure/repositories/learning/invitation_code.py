from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from shared.interfaces.repositories.learning.invitation_code import IInvitationCodeRepository
from domain.entities.users.invitation_code import InvitationCode
from infrastructure.db.models.learning.invitation_code import InvitationCodeModel


class SqlAlchemyInvitationCodeRepository(IInvitationCodeRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def _to_entity(self, row: InvitationCodeModel) -> InvitationCode:
        return InvitationCode(
            id=row.id,
            code=row.code,
            group_id=row.group_id,
            teacher_id=row.teacher_id,
            max_uses=row.max_uses,
            use_count=row.use_count,
            expires_at=row.expires_at,
            is_active=row.is_active,
            created_at=row.created_at,
        )

    def create(
        self,
        code: str,
        group_id: int,
        teacher_id: int,
        max_uses: int | None,
        expires_at: datetime | None,
    ) -> InvitationCode:
        row = InvitationCodeModel(
            code=code.upper(),
            group_id=group_id,
            teacher_id=teacher_id,
            max_uses=max_uses,
            expires_at=expires_at,
        )
        self._session.add(row)
        self._session.flush()
        self._session.refresh(row)
        return self._to_entity(row)

    def get_by_code(self, code: str) -> InvitationCode | None:
        row = self._session.execute(
            select(InvitationCodeModel).where(
                InvitationCodeModel.code == code.upper().strip()
            )
        ).scalar_one_or_none()
        return self._to_entity(row) if row else None

    def increment_use(self, code_id: int) -> None:
        row = self._session.get(InvitationCodeModel, code_id)
        if row:
            row.use_count += 1
            self._session.flush()

    def deactivate(self, code_id: int) -> None:
        row = self._session.get(InvitationCodeModel, code_id)
        if row:
            row.is_active = False
            self._session.flush()
