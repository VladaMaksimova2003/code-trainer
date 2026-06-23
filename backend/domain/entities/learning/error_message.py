from domain.entities.base import Entity
from shared.enums import ErrorType


class ErrorMessage(Entity):
    def __init__(
        self,
        id: int | None,
        text: str,
        error_type: ErrorType | str = "ERROR",
    ):
        super().__init__(id)
        self.text = text
        self.error_type = error_type

    def __str__(self):
        return f"[{self.error_type}] {self.text}"

    @classmethod
    def from_output(cls, output, error_type: str) -> list["ErrorMessage"]:
        if isinstance(output, list):
            items = [str(item).strip() for item in output if str(item).strip()]
            if not items:
                return []
            if len(items) == 1:
                return [cls(None, items[0], error_type)]
            return [cls(None, item, error_type) for item in items]

        raw = str(output or "").strip()
        if not raw:
            return []

        from infrastructure.execution.output_parser import is_lint_success_message, parse_diagnostics

        if is_lint_success_message(raw):
            return []

        diagnostics = parse_diagnostics(raw)
        if diagnostics:
            return [cls(None, line, error_type) for line in diagnostics]

        if "\n" in raw:
            return []

        return [cls(None, raw, error_type)]
