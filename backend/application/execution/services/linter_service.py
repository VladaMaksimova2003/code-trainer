from domain.entities.learning.user_solution import UserSolution
from domain.entities.learning.execution_result import ExecutionResult
from shared.enums import ExecutionResultStatus
from domain.entities.learning.error_message import ErrorMessage
from shared.interfaces.services import (
    CheckerFactoryInterface,
    LinterServiceInterface,
)


class LinterService(LinterServiceInterface):
    def __init__(self, factory: CheckerFactoryInterface):
        self._factory = factory

    async def lint(self, solution: UserSolution) -> ExecutionResult:
        # Используем фабрику, чтобы создать линтер
        output = await self._factory.create_linter(solution.language, solution.code)
        errors: list[ErrorMessage] = ErrorMessage.from_output(output, "LINTER")

        status = (
            ExecutionResultStatus.SUCCESS if not errors else ExecutionResultStatus.ERROR
        )
        result = ExecutionResult(
            status=status,
            output="",  # линтер вывод не нужен
            error="\n".join([e.text for e in errors]),
        )

        # Можно безопасно обновить решение пользователя
        solution.set_result(result)
        return result
