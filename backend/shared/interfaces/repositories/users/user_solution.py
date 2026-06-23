from abc import abstractmethod
from domain.entities.learning.user_solution import UserSolution
from shared.interfaces.repositories.base import Creatable, Gettable, Updatable


class UserSolutionRepository(
    Creatable[UserSolution],
    Gettable[UserSolution],
    Updatable[UserSolution],
):
    @abstractmethod
    def get_by_user_task_language(
        self, user_id: int, task_id: int, language: str
    ) -> UserSolution | None:
        pass
