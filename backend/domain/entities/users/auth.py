from datetime import datetime

from domain.entities.base import Entity


class AuthSession(Entity):
    def __init__(
        self,
        id: int | None,
        user_id: int,
        refresh_token_jti_hash: str,
        expires_at: datetime,
        created_at: datetime | None = None,
        revoked_at: datetime | None = None,
        rotated_from_id: int | None = None,
        user_agent: str | None = None,
        ip_address: str | None = None,
    ) -> None:
        super().__init__(id)
        self.user_id = user_id
        self.refresh_token_jti_hash = refresh_token_jti_hash
        self.expires_at = expires_at
        self.created_at = created_at or datetime.utcnow()
        self.revoked_at = revoked_at
        self.rotated_from_id = rotated_from_id
        self.user_agent = user_agent
        self.ip_address = ip_address

    @property
    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() >= self.expires_at

    @property
    def is_active(self) -> bool:
        return not self.is_revoked and not self.is_expired

    def revoke(self, revoked_at: datetime | None = None) -> None:
        if self.revoked_at is None:
            self.revoked_at = revoked_at or datetime.utcnow()
