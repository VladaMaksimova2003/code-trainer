# application/services/linter_service_interface.py
from abc import ABC, abstractmethod
from domain.entities.learning.user_solution import UserSolution
from domain.entities.learning.execution_result import ExecutionResult


class LinterServiceInterface(ABC):
    @abstractmethod
    async def lint(self, solution: UserSolution) -> ExecutionResult:
        pass
