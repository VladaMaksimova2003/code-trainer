from domain.entities.base import Entity
from domain.entities.tasks.base_task import BaseTask
from shared.enums import SolutionStatus, ExecutionResultStatus
from domain.entities.learning.execution_result import ExecutionResult


class UserSolution(Entity):

    def __init__(
        self,
        id: int | None,
        user_id: int,
        task: BaseTask,
        code: str,
        language: str,
    ):
        super().__init__(id)

        self.user_id = user_id
        self.task_id = task.id
        self.task_version = task.version
        self.code = code
        self.language = language

        self.status: SolutionStatus = SolutionStatus.NOT_STARTED
        self.result: ExecutionResult | None = None

    @staticmethod
    def create(
        user_id: int,
        task: BaseTask,
        code: str,
        language: str,
    ) -> "UserSolution":

        solution = UserSolution(
            id=None,
            user_id=user_id,
            task=task,
            code=code,
            language=language,
        )

        solution.status = SolutionStatus.IN_PROGRESS

        return solution

    def update(self, new_code: str) -> "UserSolution":
        self.code = new_code
        self.status = SolutionStatus.IN_PROGRESS
        return self

    def complete(self, result: ExecutionResult):
        self.result = result
        self.status = (
            SolutionStatus.COMPLETED
            if result.status == ExecutionResultStatus.SUCCESS
            else SolutionStatus.FAILED
        )
