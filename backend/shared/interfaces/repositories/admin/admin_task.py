from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from shared.enums import AssignmentWorkflowStatus


@dataclass(frozen=True)
class AdminAssignmentListItem:
    id: int
    title: str
    task_type: str
    difficulty: str
    teacher_id: int | None
    version: int
    workflow_status: str
    is_delete: bool
    created_at: datetime | None
    collection_title: str | None = None
    chapter_title: str | None = None
    chapter_key: str | None = None
    language: str | None = None
    chapter_slug: str | None = None
    teacher_name: str | None = None
    teacher_email: str | None = None
    teacher_is_deleted: bool = False


@dataclass(frozen=True)
class AdminAssignmentVersionItem:
    id: int
    task_id: int
    version_number: int
    title: str
    is_active: bool
    created_at: datetime | None


class IAdminTaskRepository(ABC):
    @abstractmethod
    def list_assignments(self, include_deleted: bool = True) -> list[AdminAssignmentListItem]:
        pass

    @abstractmethod
    def set_workflow_status(self, task_id: int, status: AssignmentWorkflowStatus) -> None:
        pass

    @abstractmethod
    def archive_assignment(self, task_id: int) -> None:
        pass

    @abstractmethod
    def list_versions(self, task_id: int) -> list[AdminAssignmentVersionItem]:
        pass

    @abstractmethod
    def create_version_snapshot(self, task_id: int) -> AdminAssignmentVersionItem:
        pass

    @abstractmethod
    def activate_version(self, task_id: int, version_id: int) -> None:
        pass
