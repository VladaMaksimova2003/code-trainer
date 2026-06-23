from datetime import datetime, UTC

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from shared.interfaces.repositories.users.auth_session import IAuthSessionRepository
from domain.entities.users.auth import AuthSession as DomainAuthSession
from infrastructure.db.models.user.auth_session import AuthSession as AuthSessionModel


class SqlAlchemyAuthSessionRepository(IAuthSessionRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, session: DomainAuthSession) -> DomainAuthSession:
        model = AuthSessionModel(
            user_id=session.user_id,
            jti_hash=session.refresh_token_jti_hash,
            created_at=session.created_at,
            expires_at=session.expires_at,
            revoked_at=session.revoked_at,
            rotated_from_id=session.rotated_from_id,
            ip=session.ip_address,
            user_agent=session.user_agent,
        )
        self._session.add(model)
        self._session.flush()
        self._session.refresh(model)
        return self._to_domain(model)

    def get_by_jti_hash(self, jti_hash: str) -> DomainAuthSession | None:
        stmt = select(AuthSessionModel).where(AuthSessionModel.jti_hash == jti_hash)
        model = self._session.execute(stmt).scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    def revoke(self, session_id: int) -> None:
        stmt = (
            update(AuthSessionModel)
            .where(AuthSessionModel.id == session_id)
            .values(revoked_at=datetime.now(UTC))
        )
        self._session.execute(stmt)

    def revoke_all_for_user(self, user_id: int) -> None:
        stmt = (
            update(AuthSessionModel)
            .where(
                AuthSessionModel.user_id == user_id,
                AuthSessionModel.revoked_at.is_(None),
            )
            .values(revoked_at=datetime.now(UTC))
        )
        self._session.execute(stmt)

    @staticmethod
    def _to_domain(model: AuthSessionModel) -> DomainAuthSession:
        return DomainAuthSession(
            id=model.id,
            user_id=model.user_id,
            refresh_token_jti_hash=model.jti_hash,
            created_at=model.created_at,
            expires_at=model.expires_at,
            revoked_at=model.revoked_at,
            rotated_from_id=model.rotated_from_id,
            ip_address=model.ip,
            user_agent=model.user_agent,
        )
