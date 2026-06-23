from shared.interfaces.repositories.users.user import IUserRepository
from shared.interfaces.repositories.users.user_role import IUserRoleRepository
from shared.interfaces.uow import IUnitOfWork
from shared.exceptions import UserNotFoundError
from shared.enums import UserType
from domain.entities.users.user import User


class AssignRoleToUserUseCase:
    def __init__(
        self,
        user_repository: IUserRepository[User],
        user_role_repository: IUserRoleRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._users = user_repository
        self._roles = user_role_repository
        self._uow = uow

    def execute(self, user_id: int, role: UserType) -> list[str]:
        with self._uow(autocommit=True):
            user = self._users.get(user_id)
            if user is None or user.is_deleted:
                raise UserNotFoundError("User not found")
            self._roles.assign_role(user_id, role)
            roles = self._roles.get_roles_for_user(user_id)
            return sorted(r.value for r in roles)


class RemoveRoleFromUserUseCase:
    def __init__(
        self,
        user_role_repository: IUserRoleRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._roles = user_role_repository
        self._uow = uow

    def execute(self, user_id: int, role: UserType) -> list[str]:
        with self._uow(autocommit=True):
            self._roles.remove_role(user_id, role)
            roles = self._roles.get_roles_for_user(user_id)
            return sorted(r.value for r in roles)
