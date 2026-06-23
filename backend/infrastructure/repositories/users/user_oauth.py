from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.db.models.user.user_oauth_account import UserOAuthAccount


@dataclass(frozen=True)
class LinkedOAuthAccount:
    id: int
    user_id: int
    provider: str
    provider_user_id: str
    provider_email: str | None


class SqlAlchemyUserOAuthRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_provider_account(self, provider: str, provider_user_id: str) -> LinkedOAuthAccount | None:
        stmt = select(UserOAuthAccount).where(
            UserOAuthAccount.provider == provider,
            UserOAuthAccount.provider_user_id == provider_user_id,
        )
        model = self._session.execute(stmt).scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    def create_link(
        self,
        *,
        user_id: int,
        provider: str,
        provider_user_id: str,
        provider_email: str | None,
    ) -> LinkedOAuthAccount:
        model = UserOAuthAccount(
            user_id=user_id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_email=provider_email,
        )
        self._session.add(model)
        self._session.flush()
        self._session.refresh(model)
        return self._to_domain(model)

    @staticmethod
    def _to_domain(model: UserOAuthAccount) -> LinkedOAuthAccount:
        return LinkedOAuthAccount(
            id=model.id,
            user_id=model.user_id,
            provider=model.provider,
            provider_user_id=model.provider_user_id,
            provider_email=model.provider_email,
        )
