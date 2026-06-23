from abc import ABC, abstractmethod

from domain.entities.learning.group import Group


class IGroupRepository(ABC):
    @abstractmethod
    def create(self, name: str, teacher_id: int) -> Group:
        pass

    @abstractmethod
    def get_by_id(self, group_id: int) -> Group | None:
        pass

    @abstractmethod
    def list_by_teacher(self, teacher_id: int) -> list[Group]:
        pass

    @abstractmethod
    def list_for_student(self, student_id: int) -> list[Group]:
        pass

    @abstractmethod
    def add_member(self, group_id: int, student_id: int) -> None:
        pass

    @abstractmethod
    def is_member(self, group_id: int, student_id: int) -> bool:
        pass

    @abstractmethod
    def student_teacher_ids(self, student_id: int) -> set[int]:
        """Teachers whose groups the student belongs to."""
        pass

    @abstractmethod
    def list_member_ids(self, group_id: int) -> list[int]:
        pass

    @abstractmethod
    def delete(self, group_id: int) -> bool:
        """Delete group row. Returns False if not found."""
        pass
