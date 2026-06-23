from fastapi import Depends
from sqlalchemy.orm import Session

from api.dependencies.auth import SimpleUnitOfWork
from application.tasks.services.catalog.catalog_assignment_service import CatalogAssignmentService
from application.tasks.services.catalog.catalog_service import CatalogService
from application.tasks.services.catalog.task_service import TaskService
from infrastructure.db.session import get_db
from infrastructure.repositories.tasks.task_catalog import (
    SqlAlchemyCatalogRepository,
    SqlAlchemyCatalogTaskRelationRepository,
    SqlAlchemyTaskCatalogRepository,
)


def _task_repo(db: Session = Depends(get_db)) -> SqlAlchemyTaskCatalogRepository:
    return SqlAlchemyTaskCatalogRepository(db)


def _catalog_repo(db: Session = Depends(get_db)) -> SqlAlchemyCatalogRepository:
    return SqlAlchemyCatalogRepository(db)


def _relation_repo(
    db: Session = Depends(get_db),
) -> SqlAlchemyCatalogTaskRelationRepository:
    return SqlAlchemyCatalogTaskRelationRepository(db)


def get_task_service(
    db: Session = Depends(get_db),
    tasks: SqlAlchemyTaskCatalogRepository = Depends(_task_repo),
    relations: SqlAlchemyCatalogTaskRelationRepository = Depends(_relation_repo),
) -> TaskService:
    return TaskService(tasks, relations, SimpleUnitOfWork(db))


def get_catalog_service(
    db: Session = Depends(get_db),
    catalogs: SqlAlchemyCatalogRepository = Depends(_catalog_repo),
) -> CatalogService:
    return CatalogService(catalogs, SimpleUnitOfWork(db))


def get_catalog_assignment_service(
    db: Session = Depends(get_db),
    tasks: SqlAlchemyTaskCatalogRepository = Depends(_task_repo),
    catalogs: SqlAlchemyCatalogRepository = Depends(_catalog_repo),
    relations: SqlAlchemyCatalogTaskRelationRepository = Depends(_relation_repo),
    task_service: TaskService = Depends(get_task_service),
) -> CatalogAssignmentService:
    return CatalogAssignmentService(
        tasks, catalogs, relations, task_service, SimpleUnitOfWork(db)
    )
