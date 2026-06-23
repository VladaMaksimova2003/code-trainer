from shared.interfaces.repositories.admin.teacher_role_request import (
    ITeacherRoleRequestRepository,
)
from shared.interfaces.uow import IUnitOfWork
from shared.exceptions import (
    InvalidTeacherRoleRequestStateError,
    TeacherRoleRequestNotFoundError,
)
from domain.entities.users.teacher_role_request import TeacherRoleRequest
from shared.enums import TeacherRoleRequestStatus


class RejectTeacherRoleRequestUseCase:
    def __init__(
        self,
        request_repository: ITeacherRoleRequestRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._request_repository = request_repository
        self._uow = uow

    def execute(self, request_id: int, admin_user_id: int) -> TeacherRoleRequest:
        with self._uow(autocommit=True):
            request = self._request_repository.get_by_id(request_id)
            if request is None:
                raise TeacherRoleRequestNotFoundError("Request not found.")
            if not request.is_pending():
                raise InvalidTeacherRoleRequestStateError(
                    "Only pending requests can be rejected."
                )

            return self._request_repository.update_status(
                request_id=request_id,
                status=TeacherRoleRequestStatus.REJECTED,
                reviewed_by_id=admin_user_id,
            )
