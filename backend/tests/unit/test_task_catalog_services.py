from __future__ import annotations

from datetime import datetime, timezone

import pytest

from application.tasks.services.catalog.catalog_assignment_service import CatalogAssignmentService
from application.tasks.services.catalog.catalog_service import CatalogService
from application.tasks.services.catalog.task_service import TaskService
from domain.entities.tasks.catalog import Catalog, CatalogTaskRelation, Task
from shared.exceptions import (
    CatalogNotFoundError,
    TaskAlreadyAssignedError,
    TaskNotFoundError,
)


class FakeUnitOfWork:
    def __call__(self, *, autocommit: bool = False):
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class InMemoryTaskRepository:
    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1
        self.deleted: list[int] = []

    def create(
        self,
        *,
        title: str,
        content: str,
        topic_id: int | None,
        type_id: str,
        teacher_id: int,
    ) -> Task:
        task = Task(
            id=self._next_id,
            title=title,
            content=content,
            topic_id=topic_id,
            type_id=type_id,
            created_at=datetime.now(timezone.utc),
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def get_by_id(self, task_id: int) -> Task | None:
        return self._tasks.get(task_id)

    def list_for_teacher(self, teacher_id: int) -> list[Task]:
        return list(self._tasks.values())

    def delete(self, task_id: int) -> None:
        self._tasks.pop(task_id, None)
        self.deleted.append(task_id)


class InMemoryCatalogRepository:
    def __init__(self) -> None:
        self._catalogs: dict[int, Catalog] = {}
        self._next_id = 1
        self.deleted: list[int] = []

    def create(
        self,
        *,
        title: str,
        description: str | None,
        teacher_id: int,
        visibility: str = "public",
        group_id: int | None = None,
    ) -> Catalog:
        catalog = Catalog(
            id=self._next_id,
            title=title,
            description=description,
            created_at=datetime.now(timezone.utc),
            visibility=visibility,
            group_id=group_id,
        )
        self._catalogs[catalog.id] = catalog
        self._next_id += 1
        return catalog

    def get_by_id(self, catalog_id: int) -> Catalog | None:
        return self._catalogs.get(catalog_id)

    def list_for_teacher(self, teacher_id: int) -> list[Catalog]:
        return list(self._catalogs.values())

    def delete(self, catalog_id: int) -> None:
        self._catalogs.pop(catalog_id, None)
        self.deleted.append(catalog_id)


class InMemoryRelationRepository:
    def __init__(self) -> None:
        self._relations: set[tuple[int, int]] = set()

    def assign(self, task_id: int, catalog_id: int) -> CatalogTaskRelation:
        self._relations.add((task_id, catalog_id))
        return CatalogTaskRelation(task_id=task_id, catalog_id=catalog_id)

    def remove(self, task_id: int, catalog_id: int) -> None:
        self._relations.discard((task_id, catalog_id))

    def remove_all_for_task(self, task_id: int) -> None:
        self._relations = {
            pair for pair in self._relations if pair[0] != task_id
        }

    def list_task_ids_by_catalog(self, catalog_id: int) -> list[int]:
        return sorted(
            task_id
            for task_id, cid in self._relations
            if cid == catalog_id
        )

    def list_catalog_ids_by_task(self, task_id: int) -> list[int]:
        return sorted(
            catalog_id
            for tid, catalog_id in self._relations
            if tid == task_id
        )

    def is_assigned(self, task_id: int, catalog_id: int) -> bool:
        return (task_id, catalog_id) in self._relations


@pytest.fixture
def services() -> tuple[TaskService, CatalogService, CatalogAssignmentService, InMemoryTaskRepository, InMemoryCatalogRepository, InMemoryRelationRepository]:
    uow = FakeUnitOfWork()
    tasks = InMemoryTaskRepository()
    catalogs = InMemoryCatalogRepository()
    relations = InMemoryRelationRepository()
    task_service = TaskService(tasks, relations, uow)
    catalog_service = CatalogService(catalogs, uow)
    assignment_service = CatalogAssignmentService(
        tasks, catalogs, relations, task_service, uow
    )
    return task_service, catalog_service, assignment_service, tasks, catalogs, relations


def test_flow_a_create_then_assign(services):
    task_service, catalog_service, assignment_service, tasks, catalogs, relations = services

    task = task_service.create_task(
        title="Sum",
        content="Add numbers",
        topic_id=1,
        type_id="algorithm",
        teacher_id=10,
    )
    catalog = catalog_service.create_catalog(
        title="Basics",
        description="Intro tasks",
        teacher_id=10,
    )

    assert task.id == 1
    assert catalog.id == 1
    assert relations.is_assigned(task.id, catalog.id) is False

    assignment_service.assign_task_to_catalog(task.id, catalog.id)

    assert relations.is_assigned(task.id, catalog.id) is True
    assert assignment_service.get_tasks_by_catalog(catalog.id) == [task]
    assert task.id in tasks._tasks


def test_flow_b_create_in_catalog_context(services):
    _, catalog_service, assignment_service, tasks, _, relations = services

    catalog = catalog_service.create_catalog(
        title="Week 1",
        description=None,
        teacher_id=5,
    )
    task = assignment_service.create_task_in_catalog_context(
        catalog_id=catalog.id,
        title="Hello",
        content="Print hello",
        topic_id=None,
        type_id="algorithm",
        teacher_id=5,
    )

    assert task.title == "Hello"
    assert relations.is_assigned(task.id, catalog.id)
    assert assignment_service.get_tasks_by_catalog(catalog.id) == [task]
    assert not hasattr(task, "catalog_id")


def test_delete_catalog_does_not_delete_tasks(services):
    task_service, catalog_service, assignment_service, tasks, catalogs, _ = services

    task = task_service.create_task(
        title="Keep me",
        content="",
        topic_id=None,
        type_id="algorithm",
        teacher_id=1,
    )
    catalog = catalog_service.create_catalog(
        title="Temp",
        description=None,
        teacher_id=1,
    )
    assignment_service.assign_task_to_catalog(task.id, catalog.id)

    catalog_service.delete_catalog(catalog.id)

    assert catalog.id in catalogs.deleted
    assert tasks.get_by_id(task.id) is not None


def test_delete_task_removes_relations(services):
    task_service, catalog_service, assignment_service, _, _, relations = services

    task = task_service.create_task(
        title="Gone",
        content="",
        topic_id=None,
        type_id="algorithm",
        teacher_id=1,
    )
    catalog = catalog_service.create_catalog(
        title="Set",
        description=None,
        teacher_id=1,
    )
    assignment_service.assign_task_to_catalog(task.id, catalog.id)

    task_service.delete_task(task.id)

    assert relations.list_catalog_ids_by_task(task.id) == []


def test_no_duplicate_assignment(services):
    task_service, catalog_service, assignment_service, _, _, _ = services

    task = task_service.create_task(
        title="One",
        content="",
        topic_id=None,
        type_id="algorithm",
        teacher_id=1,
    )
    catalog = catalog_service.create_catalog(
        title="Set",
        description=None,
        teacher_id=1,
    )
    assignment_service.assign_task_to_catalog(task.id, catalog.id)

    with pytest.raises(TaskAlreadyAssignedError):
        assignment_service.assign_task_to_catalog(task.id, catalog.id)


def test_get_missing_task_raises(services):
    task_service, _, _, _, _, _ = services
    with pytest.raises(TaskNotFoundError):
        task_service.get_task(999)


def test_get_missing_catalog_raises(services):
    _, catalog_service, _, _, _, _ = services
    with pytest.raises(CatalogNotFoundError):
        catalog_service.get_catalog(404)
