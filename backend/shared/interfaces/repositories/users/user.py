from abc import abstractmethod
from typing import Generic, TypeVar

from domain.entities.users.user import User
from domain.entities.users.student import Student
from shared.interfaces.repositories.base import (
    Creatable,
    Gettable,
    Updatable,
)

TUser = TypeVar("TUser", bound=User)


class UsersRepository(Creatable[TUser], Gettable[TUser], Generic[TUser]):
    @abstractmethod
    def get_by_email(self, email: str) -> TUser | None:
        pass


class StudentsRepository(UsersRepository[Student]):
    pass


class TeachersRepository(UsersRepository[User]):
    pass


IUserRepository = UsersRepository[TUser]
