from shared.interfaces.services import CheckerServiceInterface
from application.execution.dto import (
    CheckResultDTO,
    CheckSolutionDTO,
    ErrorMessageDTO,
)


class CheckSolutionUseCase:
    def __init__(self, checker: CheckerServiceInterface):
        self._checker = checker

    def execute(self, data: CheckSolutionDTO) -> CheckResultDTO:
        mode = (data.mode or "full").lower()
        run_compiler = mode in {"full", "compile_only"}
        run_linter = mode in {"full", "lint_only"}
        run_pattern = mode in {"full", "pattern_only"}

        errors = self._checker.check_code(
            data.code,
            data.language,
            data.constructions,
            run_compiler=run_compiler,
            run_linter=run_linter,
            run_pattern=run_pattern,
        )
        success = len(errors) == 0

        return CheckResultDTO(
            success=success,
            errors=[
                ErrorMessageDTO(text=e.text, error_type=str(e.error_type))
                for e in errors
            ],
            task_id=data.task_id,
        )
