from shared.interfaces.services import CheckerFactoryInterface
from application.execution.dto import (
    CheckResultDTO,
    CheckSolutionDTO,
    ErrorMessageDTO,
)
from domain.entities.learning.error_message import ErrorMessage


class LinterObserver:
    def __init__(self, factory: CheckerFactoryInterface):
        self.factory = factory

    def update(self, data: CheckSolutionDTO) -> CheckResultDTO:
        output = self.factory.create_linter(data.language, data.code)
        errors = ErrorMessage.from_output(output, "LINTER")
        success = len(errors) == 0
        return CheckResultDTO(
            success=success,
            errors=[
                ErrorMessageDTO(text=e.text, error_type=str(e.error_type))
                for e in errors
            ],
            task_id=data.task_id,
        )
