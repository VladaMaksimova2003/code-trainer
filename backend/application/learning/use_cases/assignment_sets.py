from shared.interfaces.repositories.learning.assignment_set import IAssignmentSetRepository
from shared.interfaces.repositories.learning.group import IGroupRepository
from shared.interfaces.uow import IUnitOfWork
from application.tasks.services.content_access_service import ContentAccessService
from domain.policies.rbac.rbac import normalize_role
from shared.enums import AssignmentSetVisibility, UserType
from domain.entities.tasks.assignment_set import AssignmentSet
from shared.exceptions import AccessDeniedToContentError, AssignmentSetNotFoundError, GroupNotFoundError


class CreateAssignmentSetUseCase:
    def __init__(
        self,
        sets: IAssignmentSetRepository,
        groups: IGroupRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._sets = sets
        self._groups = groups
        self._uow = uow

    def execute(
        self,
        teacher_id: int,
        name: str,
        description: str,
        visibility: AssignmentSetVisibility,
        group_id: int | None,
    ) -> AssignmentSet:
        if group_id is not None:
            group = self._groups.get_by_id(group_id)
            if group is None or group.teacher_id != teacher_id:
                raise GroupNotFoundError("Group not found")
        with self._uow(autocommit=True):
            return self._sets.create(
                name=name.strip(),
                description=description,
                teacher_id=teacher_id,
                visibility=visibility,
                group_id=group_id,
            )


class UpdateAssignmentSetUseCase:
    def __init__(self, sets: IAssignmentSetRepository, uow: IUnitOfWork) -> None:
        self._sets = sets
        self._uow = uow

    def execute(
        self,
        teacher_id: int,
        set_id: int,
        name: str | None = None,
        description: str | None = None,
        visibility: AssignmentSetVisibility | None = None,
        group_id: int | None = None,
        is_archived: bool | None = None,
    ) -> AssignmentSet:
        current = self._sets.get_by_id(set_id)
        if current is None or current.teacher_id != teacher_id:
            raise AssignmentSetNotFoundError("Assignment set not found")
        with self._uow(autocommit=True):
            return self._sets.update(
                set_id, name, description, visibility, group_id, is_archived
            )


class ListTeacherAssignmentSetsUseCase:
    def __init__(self, sets: IAssignmentSetRepository) -> None:
        self._sets = sets

    def execute(self, teacher_id: int, include_archived: bool = False) -> list[AssignmentSet]:
        return self._sets.list_for_teacher(teacher_id, include_archived)


class ListAccessibleAssignmentSetsUseCase:
    def __init__(
        self,
        access: ContentAccessService,
        sets: IAssignmentSetRepository,
    ) -> None:
        self._access = access
        self._sets = sets

    def execute(self, user_id: int | None, roles: list[str]) -> list[AssignmentSet]:
        normalized = frozenset(normalize_role(r) for r in roles)
        if user_id is None:
            return self._sets.list_discoverable_public()
        accessible_ids = {
            s.id for s in self._access.accessible_assignment_sets_for_user(user_id, normalized)
        }
        public = self._sets.list_discoverable_public()
        result: dict[int, AssignmentSet] = {s.id: s for s in public}
        for set_id in accessible_ids:
            if set_id not in result:
                row = self._sets.get_by_id(set_id)
                if row and not row.is_archived:
                    result[row.id] = row
        return list(result.values())


class GetAssignmentSetUseCase:
    def __init__(
        self,
        sets: IAssignmentSetRepository,
        access: ContentAccessService,
    ) -> None:
        self._sets = sets
        self._access = access

    def execute(
        self, user_id: int | None, roles: list[str], set_id: int
    ) -> AssignmentSet:
        row = self._sets.get_by_id(set_id)
        if row is None:
            raise AssignmentSetNotFoundError("Assignment set not found")
        normalized = frozenset(normalize_role(r) for r in roles)
        if not self._access.can_access_assignment_set(user_id, normalized, set_id):
            raise AccessDeniedToContentError("Access denied")
        return row


class ManageAssignmentSetItemsUseCase:
    def __init__(self, sets: IAssignmentSetRepository, uow: IUnitOfWork) -> None:
        self._sets = sets
        self._uow = uow

    def add(self, teacher_id: int, set_id: int, task_id: int, sort_order: int, topic: str | None):
        current = self._sets.get_by_id(set_id)
        if current is None or current.teacher_id != teacher_id:
            raise AssignmentSetNotFoundError("Assignment set not found")
        with self._uow(autocommit=True):
            return self._sets.add_item(set_id, task_id, sort_order, topic)

    def remove(self, teacher_id: int, set_id: int, task_id: int) -> None:
        current = self._sets.get_by_id(set_id)
        if current is None or current.teacher_id != teacher_id:
            raise AssignmentSetNotFoundError("Assignment set not found")
        with self._uow(autocommit=True):
            self._sets.remove_item(set_id, task_id)
