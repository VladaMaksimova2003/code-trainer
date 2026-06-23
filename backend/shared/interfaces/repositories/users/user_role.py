from abc import ABC, abstractmethod

from shared.enums import UserType


class IUserRoleRepository(ABC):
    @abstractmethod
    def get_roles_for_user(self, user_id: int) -> frozenset[UserType]:
        pass

    @abstractmethod
    def assign_role(self, user_id: int, role: UserType) -> None:
        pass

    @abstractmethod
    def sync_primary_role_column(self, user_id: int, roles: frozenset[UserType]) -> None:
        """Keep legacy user.role column aligned with highest-priority role."""
        pass

    @abstractmethod
    def remove_role(self, user_id: int, role: UserType) -> None:
        pass
