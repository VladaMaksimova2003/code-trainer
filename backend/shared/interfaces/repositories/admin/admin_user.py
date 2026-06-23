from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from shared.enums import UserType


@dataclass(frozen=True)
class AdminUserListItem:
    id: int
    name: str
    email: str
    roles: list[str]
    is_blocked: bool
    is_deleted: bool
    created_at: datetime | None


@dataclass(frozen=True)
class AdminUserDetail(AdminUserListItem):
    total_submissions: int
    successful_submissions: int
    solved_tasks_count: int
    last_login_at: datetime | None = None
    created_tasks_count: int | None = None
    created_catalogs_count: int | None = None
    groups_count: int | None = None
    about: str | None = None
    success_rate: float = 0.0
    streak_days: int = 0
    member_groups_count: int = 0
    member_group_names: list[str] | None = None


class IAdminUserRepository(ABC):
    @abstractmethod
    def list_users(self, include_deleted: bool = False) -> list[AdminUserListItem]:
        pass

    @abstractmethod
    def get_user_detail(self, user_id: int) -> AdminUserDetail | None:
        pass

    @abstractmethod
    def set_blocked(self, user_id: int, blocked: bool) -> None:
        pass

    @abstractmethod
    def soft_delete(self, user_id: int) -> None:
        pass
