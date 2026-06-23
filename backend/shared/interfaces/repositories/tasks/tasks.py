from abc import abstractmethod
from typing import Generic, TypeVar
from shared.interfaces.repositories.base import (
    Creatable,
    Gettable,
    Updatable,
    Listable,
)
from domain.entities.tasks.translation_task import TranslationTask
from domain.entities.tasks.base_task import BaseTask

TTask = TypeVar("TTask", bound=BaseTask)


class TasksRepository(Gettable[TTask], Listable[TTask], Generic[TTask]):
    @abstractmethod
    def get_by_difficulty(self, difficulty) -> list[TTask]:
        pass


class TranslationTasksRepository(
    Creatable[TranslationTask],
    Updatable[TranslationTask],
    TasksRepository[TranslationTask],
):
    pass
