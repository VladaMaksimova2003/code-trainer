from abc import ABC, abstractmethod

from domain.entities.learning.error_message import ErrorMessage


class CheckerServiceInterface(ABC):
    @abstractmethod
    def check_code(
        self,
        code: str,
        language: str,
        constructions: list[str],
        run_compiler: bool = True,
        run_linter: bool = True,
        run_pattern: bool = True,
    ) -> list[ErrorMessage]:
        pass
