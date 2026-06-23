from shared.interfaces.repositories.users.user import IUserRepository
from shared.interfaces.repositories.users.user_role import IUserRoleRepository
from application.auth.dto import CurrentUserResult
from shared.exceptions import InvalidTokenError
from domain.policies.rbac.rbac import primary_role
from domain.entities.users.user import User


class GetCurrentUserUseCase:
    def __init__(
        self,
        user_repository: IUserRepository[User],
        user_role_repository: IUserRoleRepository,
    ) -> None:
        self._user_repository = user_repository
        self._user_role_repository = user_role_repository

    def execute(self, user_id: int) -> CurrentUserResult:
        user = self._user_repository.get(user_id)
        if user is None:
            raise InvalidTokenError("User not found.")

        roles = self._user_role_repository.get_roles_for_user(user_id)
        role_list = sorted(roles, key=lambda r: r.value)

        return CurrentUserResult(
            id=user.id,
            name=user.name,
            email=user.email,
            role=primary_role(roles),
            roles=role_list,
        )
