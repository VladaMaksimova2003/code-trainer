from infrastructure.repositories.converters.base import Converter
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select, delete
from typing import Type, TypeVar
from shared.exceptions import (
    CannotDeleteEntityError,
    EntityNotFoundError,
)


TEntity = TypeVar("TEntity")
Base = TypeVar("Base")


class SqlAlchemyRepository:
    def __init__(self, session: Session) -> None:
        self._session = session


class GenericSqlAlchemyRepository(
    SqlAlchemyRepository,
):
    def __init__(
        self, session: Session, converter: Converter, model: Type[Base]
    ) -> None:
        super().__init__(session)
        self._converter = converter
        self._model = model

    def create(self, entity: TEntity) -> TEntity:
        model = self._converter.to_model(entity)
        self._session.add(model)
        self._session.flush([model])
        return self._converter.to_entity(model)

    def update(self, entity: TEntity) -> TEntity:
        model = self._converter.to_model(entity)
        merged_model = self._session.merge(model)
        self._session.flush([merged_model])
        return self._converter.to_entity(merged_model)

    def delete(self, entity_id: int) -> None:
        stmt = delete(self._model).where(self._model.id == entity_id)
        try:
            self._session.execute(stmt)
        except IntegrityError:
            raise CannotDeleteEntityError()

    def get(self, entity_id: int) -> TEntity:
        stmt = select(self._model).filter_by(id=entity_id)
        result = self._session.execute(stmt)
        model = result.scalars().one_or_none()
        if not model:
            raise EntityNotFoundError(self._model)
        return self._converter.to_entity(model)
