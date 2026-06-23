from shared.interfaces.repositories.admin.teacher_role_request import (
    ITeacherRoleRequestRepository,
)
from domain.entities.users.teacher_role_request import TeacherRoleRequest
from shared.enums import TeacherRoleRequestStatus


class ListTeacherRoleRequestsUseCase:
    def __init__(self, request_repository: ITeacherRoleRequestRepository) -> None:
        self._request_repository = request_repository

    def execute(
        self, status: TeacherRoleRequestStatus | None = None
    ) -> list[TeacherRoleRequest]:
        return self._request_repository.list_by_status(status)
