from shared.interfaces.repositories.admin.teacher_role_request import (
    ITeacherRoleRequestRepository,
)
from shared.interfaces.repositories.users.user_role import IUserRoleRepository
from shared.interfaces.uow import IUnitOfWork
from shared.exceptions import (
    InvalidTeacherRoleRequestStateError,
    TeacherRoleRequestNotFoundError,
)
from domain.entities.users.teacher_role_request import TeacherRoleRequest
from shared.enums import TeacherRoleRequestStatus, UserType


class ApproveTeacherRoleRequestUseCase:
    def __init__(
        self,
        request_repository: ITeacherRoleRequestRepository,
        user_role_repository: IUserRoleRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._request_repository = request_repository
        self._user_role_repository = user_role_repository
        self._uow = uow

    def execute(self, request_id: int, admin_user_id: int) -> TeacherRoleRequest:
        with self._uow(autocommit=True):
            request = self._request_repository.get_by_id(request_id)
            if request is None:
                raise TeacherRoleRequestNotFoundError("Request not found.")
            if not request.is_pending():
                raise InvalidTeacherRoleRequestStateError(
                    "Only pending requests can be approved."
                )

            self._user_role_repository.assign_role(request.user_id, UserType.STUDENT)
            self._user_role_repository.assign_role(request.user_id, UserType.TEACHER)

            return self._request_repository.update_status(
                request_id=request_id,
                status=TeacherRoleRequestStatus.APPROVED,
                reviewed_by_id=admin_user_id,
            )
