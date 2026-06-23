from sqlalchemy.orm import Session, joinedload
from sqlalchemy import Select, select
from shared.interfaces.repositories.tasks.tasks import TasksRepository
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.repositories.base import (
    GenericSqlAlchemyRepository,
    SqlAlchemyRepository,
)
from infrastructure.repositories.converters.task import SqlAlchemyTaskConverter
from domain.entities.tasks.base_task import BaseTask


class SqlAlchemyTasksRepository(
    SqlAlchemyRepository,
):
    def __init__(self, session: Session) -> None:
        super().__init__(session)
        self._converter = SqlAlchemyTaskConverter
        self._model = TaskModel
        self._generic_repository: GenericSqlAlchemyRepository[BaseTask] = (
            GenericSqlAlchemyRepository(self._session, self._converter, self._model)
        )

    def get(self, entity_id: int) -> BaseTask:
        stmt = select(self._model).filter_by(id=entity_id)
        stmt = self._join_dependencies(stmt)
        result = self._session.execute(stmt)
        model = result.scalars().unique().one_or_none()
        if not model:
            raise TaskNotFoundError()
        return self._converter.to_entity(model)

    def _join_dependencies(self, stmt: Select) -> Select:
        return stmt.options(
            joinedload(self._model.constructions),
        )
