from abc import ABC, abstractmethod
from datetime import datetime

from domain.entities.users.invitation_code import InvitationCode


class IInvitationCodeRepository(ABC):
    @abstractmethod
    def create(
        self,
        code: str,
        group_id: int,
        teacher_id: int,
        max_uses: int | None,
        expires_at: datetime | None,
    ) -> InvitationCode:
        pass

    @abstractmethod
    def get_by_code(self, code: str) -> InvitationCode | None:
        pass

    @abstractmethod
    def increment_use(self, code_id: int) -> None:
        pass

    @abstractmethod
    def deactivate(self, code_id: int) -> None:
        pass
