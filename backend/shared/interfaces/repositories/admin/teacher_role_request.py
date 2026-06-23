from abc import ABC, abstractmethod

from domain.entities.users.teacher_role_request import TeacherRoleRequest
from shared.enums import TeacherRoleRequestStatus


class ITeacherRoleRequestRepository(ABC):
    @abstractmethod
    def create(self, user_id: int, message: str | None = None) -> TeacherRoleRequest:
        pass

    @abstractmethod
    def get_by_id(self, request_id: int) -> TeacherRoleRequest | None:
        pass

    @abstractmethod
    def get_pending_for_user(self, user_id: int) -> TeacherRoleRequest | None:
        pass

    @abstractmethod
    def list_by_status(
        self, status: TeacherRoleRequestStatus | None = None
    ) -> list[TeacherRoleRequest]:
        pass

    @abstractmethod
    def update_status(
        self,
        request_id: int,
        status: TeacherRoleRequestStatus,
        reviewed_by_id: int,
    ) -> TeacherRoleRequest:
        pass
