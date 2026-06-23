from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from domain.entities.base import Entity
from infrastructure.db.models.base import Base

TEntity = TypeVar("TEntity", bound=Entity)
TModel = TypeVar("TModel", bound=Base)


class Converter(ABC, Generic[TEntity, TModel]):
    @abstractmethod
    def to_entity(self, model: TModel) -> TEntity:
        pass

    @abstractmethod
    def to_model(self, entity: TEntity) -> TModel:
        pass
