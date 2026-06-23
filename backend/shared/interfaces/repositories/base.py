from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar, Literal

TEntity = TypeVar("TEntity")


class Creatable(ABC, Generic[TEntity]):
    @abstractmethod
    def create(self, entity: TEntity) -> TEntity:
        pass


class Updatable(ABC, Generic[TEntity]):
    @abstractmethod
    def update(self, entity: TEntity) -> None:
        pass


class Deletable(ABC):
    @abstractmethod
    def delete(self, entity_id: int) -> None:
        pass


class Gettable(ABC, Generic[TEntity]):
    @abstractmethod
    def get(self, entity_id: int) -> TEntity:
        pass


class Listable(ABC, Generic[TEntity]):
    @abstractmethod
    def get_list(self) -> list[TEntity]:
        pass
