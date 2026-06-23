from __future__ import annotations

from shared.interfaces.repositories.tasks.task_catalog import ITaskRepository
from shared.interfaces.uow import IUnitOfWork
from domain.entities.tasks.catalog import Task
from shared.exceptions import TaskNotFoundError


class TaskService:
    """Pure use-case service for task lifecycle (independent of catalogs)."""

    def __init__(
        self,
        tasks: ITaskRepository,
        relations: "ICatalogTaskRelationRepository",
        uow: IUnitOfWork,
    ) -> None:
        from shared.interfaces.repositories.tasks.task_catalog import (
            ICatalogTaskRelationRepository,
        )

        self._tasks = tasks
        self._relations = relations
        self._uow = uow

    def create_task(
        self,
        *,
        title: str,
        content: str,
        topic_id: int | None,
        type_id: str,
        teacher_id: int,
    ) -> Task:
        with self._uow(autocommit=True):
            return self._tasks.create(
                title=title.strip(),
                content=content,
                topic_id=topic_id,
                type_id=type_id,
                teacher_id=teacher_id,
            )

    def get_task(self, task_id: int) -> Task:
        task = self._tasks.get_by_id(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return task

    def list_tasks(self, teacher_id: int) -> list[Task]:
        return self._tasks.list_for_teacher(teacher_id)

    def delete_task(self, task_id: int) -> None:
        if self._tasks.get_by_id(task_id) is None:
            raise TaskNotFoundError(f"Task {task_id} not found")
        with self._uow(autocommit=True):
            self._relations.remove_all_for_task(task_id)
            self._tasks.delete(task_id)
