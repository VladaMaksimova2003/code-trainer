from domain.entities.base import Entity
from shared.enums import ExecutionResultStatus


class ExecutionResult:
    def __init__(
        self, status: ExecutionResultStatus, output: str = "", error: str = ""
    ):
        self.status = status
        self.output = output
        self.error = error

    def get_error_lines(self) -> list[str]:
        return [line.strip() for line in self.error.splitlines() if line.strip()]
