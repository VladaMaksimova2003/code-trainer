from __future__ import annotations

from shared.interfaces.repositories.tasks.task_catalog import (
    ICatalogRepository,
    ICatalogTaskRelationRepository,
    ITaskRepository,
)
from shared.interfaces.uow import IUnitOfWork
from application.tasks.services.catalog.task_service import TaskService
from domain.entities.tasks.catalog import CatalogTaskRelation, Task
from shared.exceptions import (
    CatalogNotFoundError,
    TaskAlreadyAssignedError,
    TaskNotFoundError,
)


class CatalogAssignmentService:
    """Manages task↔catalog relations without duplicating task records."""

    def __init__(
        self,
        tasks: ITaskRepository,
        catalogs: ICatalogRepository,
        relations: ICatalogTaskRelationRepository,
        task_service: TaskService,
        uow: IUnitOfWork,
    ) -> None:
        self._tasks = tasks
        self._catalogs = catalogs
        self._relations = relations
        self._task_service = task_service
        self._uow = uow

    def assign_task_to_catalog(self, task_id: int, catalog_id: int) -> CatalogTaskRelation:
        if self._tasks.get_by_id(task_id) is None:
            raise TaskNotFoundError(f"Task {task_id} not found")
        if self._catalogs.get_by_id(catalog_id) is None:
            raise CatalogNotFoundError(f"Catalog {catalog_id} not found")
        if self._relations.is_assigned(task_id, catalog_id):
            raise TaskAlreadyAssignedError(
                f"Task {task_id} is already in catalog {catalog_id}"
            )
        with self._uow(autocommit=True):
            return self._relations.assign(task_id, catalog_id)

    def remove_task_from_catalog(self, task_id: int, catalog_id: int) -> None:
        if not self._relations.is_assigned(task_id, catalog_id):
            raise TaskNotFoundError(
                f"Task {task_id} is not assigned to catalog {catalog_id}"
            )
        with self._uow(autocommit=True):
            self._relations.remove(task_id, catalog_id)

    def get_tasks_by_catalog(self, catalog_id: int) -> list[Task]:
        if self._catalogs.get_by_id(catalog_id) is None:
            raise CatalogNotFoundError(f"Catalog {catalog_id} not found")
        task_ids = self._relations.list_task_ids_by_catalog(catalog_id)
        tasks: list[Task] = []
        for task_id in task_ids:
            task = self._tasks.get_by_id(task_id)
            if task is not None:
                tasks.append(task)
        return sorted(
            tasks,
            key=lambda task: (
                task.chapter_order if task.chapter_order is not None else 999,
                task.display_order if task.display_order is not None else 999_999,
                task.id,
            ),
        )

    def create_task_in_catalog_context(
        self,
        *,
        catalog_id: int,
        title: str,
        content: str,
        topic_id: int | None,
        type_id: str,
        teacher_id: int,
    ) -> Task:
        """FLOW B: create task then assign — catalogId is context only, not stored on Task."""
        if self._catalogs.get_by_id(catalog_id) is None:
            raise CatalogNotFoundError(f"Catalog {catalog_id} not found")
        with self._uow(autocommit=True):
            task = self._tasks.create(
                title=title.strip(),
                content=content,
                topic_id=topic_id,
                type_id=type_id,
                teacher_id=teacher_id,
            )
            self._relations.assign(task.id, catalog_id)
            return task

    def catalog_ids_for_task(self, task_id: int) -> list[int]:
        return self._relations.list_catalog_ids_by_task(task_id)
