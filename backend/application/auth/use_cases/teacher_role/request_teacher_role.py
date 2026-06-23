from shared.interfaces.repositories.admin.teacher_role_request import (
    ITeacherRoleRequestRepository,
)
from shared.interfaces.repositories.users.user import IUserRepository
from shared.interfaces.repositories.users.user_role import IUserRoleRepository
from shared.interfaces.uow import IUnitOfWork
from shared.exceptions import (
    TeacherRoleRequestAlreadyPendingError,
    UserAlreadyHasTeacherRoleError,
)
from domain.entities.users.teacher_role_request import TeacherRoleRequest
from shared.enums import UserType
from domain.entities.users.user import User


class RequestTeacherRoleUseCase:
    def __init__(
        self,
        user_repository: IUserRepository[User],
        user_role_repository: IUserRoleRepository,
        request_repository: ITeacherRoleRequestRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._user_repository = user_repository
        self._user_role_repository = user_role_repository
        self._request_repository = request_repository
        self._uow = uow

    def execute(self, user_id: int, message: str | None = None) -> TeacherRoleRequest:
        with self._uow(autocommit=True):
            user = self._user_repository.get(user_id)
            if user is None:
                raise ValueError("User not found")

            roles = self._user_role_repository.get_roles_for_user(user_id)
            if UserType.TEACHER in roles or UserType.ADMIN in roles:
                raise UserAlreadyHasTeacherRoleError(
                    "User already has teacher or admin role."
                )

            pending = self._request_repository.get_pending_for_user(user_id)
            if pending is not None:
                raise TeacherRoleRequestAlreadyPendingError(
                    "A pending teacher role request already exists."
                )

            return self._request_repository.create(user_id=user_id, message=message)
