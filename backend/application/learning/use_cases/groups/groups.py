import secrets
from datetime import datetime, timedelta, timezone

from shared.interfaces.repositories.learning.group import IGroupRepository
from shared.interfaces.repositories.learning.invitation_code import IInvitationCodeRepository
from shared.interfaces.uow import IUnitOfWork
from shared.exceptions import (
    AlreadyGroupMemberError,
    GroupNotFoundError,
    InvalidInvitationCodeError,
)
from domain.entities.learning.group import Group


class CreateGroupUseCase:
    def __init__(
        self,
        groups: IGroupRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._groups = groups
        self._uow = uow

    def execute(self, teacher_id: int, name: str) -> Group:
        with self._uow(autocommit=True):
            return self._groups.create(name=name.strip(), teacher_id=teacher_id)


class ListTeacherGroupsUseCase:
    def __init__(self, groups: IGroupRepository) -> None:
        self._groups = groups

    def execute(self, teacher_id: int) -> list[Group]:
        return self._groups.list_by_teacher(teacher_id)


class ListStudentGroupsUseCase:
    def __init__(self, groups: IGroupRepository) -> None:
        self._groups = groups

    def execute(self, student_id: int) -> list[Group]:
        return self._groups.list_for_student(student_id)


class GenerateInvitationCodeUseCase:
    def __init__(
        self,
        groups: IGroupRepository,
        invitations: IInvitationCodeRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._groups = groups
        self._invitations = invitations
        self._uow = uow

    def execute(
        self,
        teacher_id: int,
        group_id: int,
        max_uses: int | None = None,
        expires_in_days: int | None = 30,
    ):
        group = self._groups.get_by_id(group_id)
        if group is None or group.teacher_id != teacher_id:
            raise GroupNotFoundError("Group not found")
        code = secrets.token_urlsafe(8)[:12].upper()
        expires_at = None
        if expires_in_days:
            expires_at = datetime.now(timezone.utc) + timedelta(days=expires_in_days)
        with self._uow(autocommit=True):
            return self._invitations.create(
                code=code,
                group_id=group_id,
                teacher_id=teacher_id,
                max_uses=max_uses,
                expires_at=expires_at,
            )


class JoinGroupByInvitationUseCase:
    def __init__(
        self,
        groups: IGroupRepository,
        invitations: IInvitationCodeRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._groups = groups
        self._invitations = invitations
        self._uow = uow

    def execute(self, student_id: int, code: str) -> Group:
        invitation = self._invitations.get_by_code(code)
        now = datetime.now(timezone.utc)
        if (
            invitation is None
            or not invitation.is_active
            or invitation.is_expired(now)
            or not invitation.has_uses_left()
        ):
            raise InvalidInvitationCodeError("Invalid or expired invitation code")

        group = self._groups.get_by_id(invitation.group_id)
        if group is None:
            raise GroupNotFoundError("Group not found")

        if self._groups.is_member(group.id, student_id):
            raise AlreadyGroupMemberError("Already a member of this group")

        with self._uow(autocommit=True):
            self._groups.add_member(group.id, student_id)
            self._invitations.increment_use(invitation.id)
            if invitation.max_uses is not None and invitation.use_count + 1 >= invitation.max_uses:
                self._invitations.deactivate(invitation.id)
        return group


class DeleteGroupUseCase:
    def __init__(
        self,
        groups: IGroupRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._groups = groups
        self._uow = uow

    def execute(self, teacher_id: int, group_id: int) -> None:
        group = self._groups.get_by_id(group_id)
        if group is None or group.teacher_id != teacher_id:
            raise GroupNotFoundError("Group not found")
        with self._uow(autocommit=True):
            if not self._groups.delete(group_id):
                raise GroupNotFoundError("Group not found")
