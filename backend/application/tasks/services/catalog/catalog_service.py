from __future__ import annotations

from shared.interfaces.repositories.tasks.task_catalog import ICatalogRepository
from shared.interfaces.uow import IUnitOfWork
from domain.entities.tasks.catalog import Catalog
from shared.exceptions import CatalogNotFoundError


class CatalogService:
    """Pure use-case service for catalog lifecycle (does not own tasks)."""

    def __init__(self, catalogs: ICatalogRepository, uow: IUnitOfWork) -> None:
        self._catalogs = catalogs
        self._uow = uow

    def create_catalog(
        self,
        *,
        title: str,
        description: str | None,
        teacher_id: int,
        visibility: str = "public",
        group_id: int | None = None,
    ) -> Catalog:
        with self._uow(autocommit=True):
            return self._catalogs.create(
                title=title.strip(),
                description=description,
                teacher_id=teacher_id,
                visibility=visibility,
                group_id=group_id,
            )

    def get_catalog(self, catalog_id: int) -> Catalog:
        catalog = self._catalogs.get_by_id(catalog_id)
        if catalog is None:
            raise CatalogNotFoundError(f"Catalog {catalog_id} not found")
        return catalog

    def list_catalogs(self, teacher_id: int) -> list[Catalog]:
        return self._catalogs.list_for_teacher(teacher_id)

    def delete_catalog(self, catalog_id: int) -> None:
        if self._catalogs.get_by_id(catalog_id) is None:
            raise CatalogNotFoundError(f"Catalog {catalog_id} not found")
        with self._uow(autocommit=True):
            self._catalogs.delete(catalog_id)
