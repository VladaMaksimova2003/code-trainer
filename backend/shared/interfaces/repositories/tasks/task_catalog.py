from __future__ import annotations

from abc import ABC, abstractmethod

from domain.entities.tasks.catalog import Catalog, CatalogTaskRelation, Task


class ITaskRepository(ABC):
    @abstractmethod
    def create(
        self,
        *,
        title: str,
        content: str,
        topic_id: int | None,
        type_id: str,
        teacher_id: int,
    ) -> Task:
        pass

    @abstractmethod
    def get_by_id(self, task_id: int) -> Task | None:
        pass

    @abstractmethod
    def list_for_teacher(self, teacher_id: int) -> list[Task]:
        pass

    @abstractmethod
    def delete(self, task_id: int) -> None:
        pass


class ICatalogRepository(ABC):
    @abstractmethod
    def create(
        self,
        *,
        title: str,
        description: str | None,
        teacher_id: int,
        visibility: str = "public",
        group_id: int | None = None,
    ) -> Catalog:
        pass

    @abstractmethod
    def get_by_id(self, catalog_id: int) -> Catalog | None:
        pass

    @abstractmethod
    def list_for_teacher(self, teacher_id: int) -> list[Catalog]:
        pass

    @abstractmethod
    def delete(self, catalog_id: int) -> None:
        pass


class ICatalogTaskRelationRepository(ABC):
    @abstractmethod
    def assign(self, task_id: int, catalog_id: int) -> CatalogTaskRelation:
        pass

    @abstractmethod
    def remove(self, task_id: int, catalog_id: int) -> None:
        pass

    @abstractmethod
    def remove_all_for_task(self, task_id: int) -> None:
        pass

    @abstractmethod
    def list_task_ids_by_catalog(self, catalog_id: int) -> list[int]:
        pass

    @abstractmethod
    def list_catalog_ids_by_task(self, task_id: int) -> list[int]:
        pass

    @abstractmethod
    def is_assigned(self, task_id: int, catalog_id: int) -> bool:
        pass
