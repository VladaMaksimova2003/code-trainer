from abc import ABC, abstractmethod

from shared.interfaces.repositories.tasks.tasks import (
    TranslationTasksRepository,
    TasksRepository,
)
from shared.interfaces.repositories.users.user import (
    StudentsRepository,
    TeachersRepository,
)
from shared.interfaces.repositories.users.user_solution import UserSolutionRepository


class UnitOfWork(ABC):
    students: StudentsRepository
    teachers: TeachersRepository
    tasks: TasksRepository
    user_solutions: UserSolutionRepository

    translation_tasks: TranslationTasksRepository

    def __init__(self):
        self._autocommit: bool = False

    def __call__(self, autocommit: bool = False) -> "UnitOfWork":
        self._autocommit = autocommit
        return self

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.rollback()
        elif self._autocommit:
            self.commit()
        self.shutdown()

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass

    @abstractmethod
    def shutdown(self) -> None:
        pass


IUnitOfWork = UnitOfWork
