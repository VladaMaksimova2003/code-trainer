from shared.exceptions import InfrastructureException
from typing import Type


class RepositoryException(InfrastructureException):
    pass


class EntityNotFoundError(RepositoryException):
    def __init__(self, model: Type) -> None:
        message = f"Entity({model.__name__}) not found."
        super().__init__(message)


class CannotDeleteEntityError(RepositoryException):
    def __init__(self) -> None:
        super().__init__("Cannot delete entity.")


class UserNotFound(EntityNotFoundError):
    pass


class StudentNotFoundError(UserNotFound):
    def __init__(self) -> None:
        super().__init__("Student not found.")
