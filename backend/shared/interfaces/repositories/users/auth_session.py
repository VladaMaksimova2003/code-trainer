from abc import ABC, abstractmethod

from domain.entities.users.auth import AuthSession


class IAuthSessionRepository(ABC):
    @abstractmethod
    def create(self, session: AuthSession) -> AuthSession:
        pass

    @abstractmethod
    def get_by_jti_hash(self, jti_hash: str) -> AuthSession | None:
        pass

    @abstractmethod
    def revoke(self, session_id: int) -> None:
        pass

    @abstractmethod
    def revoke_all_for_user(self, user_id: int) -> None:
        pass
