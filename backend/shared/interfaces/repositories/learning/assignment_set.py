from abc import ABC, abstractmethod

from shared.enums import AssignmentSetVisibility
from domain.entities.tasks.assignment_set import AssignmentSet, AssignmentSetItem


class IAssignmentSetRepository(ABC):
    @abstractmethod
    def create(
        self,
        name: str,
        description: str,
        teacher_id: int,
        visibility: AssignmentSetVisibility,
        group_id: int | None,
    ) -> AssignmentSet:
        pass

    @abstractmethod
    def get_by_id(self, set_id: int) -> AssignmentSet | None:
        pass

    @abstractmethod
    def update(
        self,
        set_id: int,
        name: str | None,
        description: str | None,
        visibility: AssignmentSetVisibility | None,
        group_id: int | None,
        is_archived: bool | None,
    ) -> AssignmentSet:
        pass

    @abstractmethod
    def list_for_teacher(self, teacher_id: int, include_archived: bool = False) -> list[AssignmentSet]:
        pass

    @abstractmethod
    def list_discoverable_public(self) -> list[AssignmentSet]:
        pass

    @abstractmethod
    def add_item(
        self, set_id: int, task_id: int, sort_order: int, topic: str | None
    ) -> AssignmentSetItem:
        pass

    @abstractmethod
    def remove_item(self, set_id: int, task_id: int) -> None:
        pass

    @abstractmethod
    def task_ids_in_set(self, set_id: int) -> list[int]:
        pass

    @abstractmethod
    def sets_containing_task(self, task_id: int) -> list[AssignmentSet]:
        pass

    @abstractmethod
    def count_by_teacher(self, teacher_id: int) -> int:
        pass
