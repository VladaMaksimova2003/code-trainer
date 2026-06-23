from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from domain.value_objects.auth import TokenPair
from domain.policies.rbac.role import Role


class IPasswordHasher(ABC):
    @abstractmethod
    def hash(self, raw_password: str) -> str:
        pass

    @abstractmethod
    def verify(self, raw_password: str, password_hash: str) -> bool:
        pass


class ITokenProvider(ABC):
    @abstractmethod
    def create_access_token(self, user_id: int, role: Role) -> str:
        pass

    @abstractmethod
    def create_refresh_token(
        self, user_id: int, role: Role
    ) -> tuple[str, str, datetime]:
        """Returns refresh_token, jti, expires_at."""
        pass

    @abstractmethod
    def decode_access_token(self, token: str) -> dict[str, Any]:
        pass

    @abstractmethod
    def decode_refresh_token(self, token: str) -> dict[str, Any]:
        pass
