from shared.interfaces.repositories.admin.admin_task import (
    AdminAssignmentListItem,
    AdminAssignmentVersionItem,
    IAdminTaskRepository,
)
from shared.interfaces.uow import IUnitOfWork
from shared.enums import AssignmentWorkflowStatus


class ListAssignmentsUseCase:
    def __init__(self, repo: IAdminTaskRepository, uow: IUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def execute(self, include_deleted: bool = True) -> list[AdminAssignmentListItem]:
        with self._uow():
            return self._repo.list_assignments(include_deleted=include_deleted)


class SetAssignmentWorkflowStatusUseCase:
    def __init__(self, repo: IAdminTaskRepository, uow: IUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def execute(self, task_id: int, status: AssignmentWorkflowStatus) -> None:
        with self._uow(autocommit=True):
            self._repo.set_workflow_status(task_id, status)


class ArchiveAssignmentUseCase:
    def __init__(self, repo: IAdminTaskRepository, uow: IUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def execute(self, task_id: int) -> None:
        with self._uow(autocommit=True):
            self._repo.archive_assignment(task_id)


class ListAssignmentVersionsUseCase:
    def __init__(self, repo: IAdminTaskRepository, uow: IUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def execute(self, task_id: int) -> list[AdminAssignmentVersionItem]:
        with self._uow():
            return self._repo.list_versions(task_id)


class CreateAssignmentVersionUseCase:
    def __init__(self, repo: IAdminTaskRepository, uow: IUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def execute(self, task_id: int) -> AdminAssignmentVersionItem:
        with self._uow(autocommit=True):
            return self._repo.create_version_snapshot(task_id)


class ActivateAssignmentVersionUseCase:
    def __init__(self, repo: IAdminTaskRepository, uow: IUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def execute(self, task_id: int, version_id: int) -> None:
        with self._uow(autocommit=True):
            self._repo.activate_version(task_id, version_id)
