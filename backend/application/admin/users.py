from shared.interfaces.repositories.admin.admin_user import (
    AdminUserDetail,
    AdminUserListItem,
    IAdminUserRepository,
)
from shared.interfaces.uow import IUnitOfWork


class ListUsersUseCase:
    def __init__(self, repo: IAdminUserRepository, uow: IUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def execute(self, include_deleted: bool = False) -> list[AdminUserListItem]:
        with self._uow():
            return self._repo.list_users(include_deleted=include_deleted)


class GetUserDetailUseCase:
    def __init__(self, repo: IAdminUserRepository, uow: IUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def execute(self, user_id: int) -> AdminUserDetail:
        with self._uow():
            detail = self._repo.get_user_detail(user_id)
            if detail is None:
                raise ValueError("User not found")
            return detail


class SetUserBlockedUseCase:
    def __init__(self, repo: IAdminUserRepository, uow: IUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def execute(self, user_id: int, blocked: bool) -> None:
        with self._uow(autocommit=True):
            self._repo.set_blocked(user_id, blocked)


class DeleteUserUseCase:
    def __init__(self, repo: IAdminUserRepository, uow: IUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def execute(self, user_id: int) -> None:
        with self._uow(autocommit=True):
            self._repo.soft_delete(user_id)
