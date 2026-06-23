from shared.interfaces.services import (
    CheckerFactoryInterface,
    CheckerServiceInterface,
)
from domain.entities.learning.error_message import ErrorMessage


class CheckerService(CheckerServiceInterface):
    def __init__(self, factory: CheckerFactoryInterface):
        self._factory = factory

    def check_code(
        self,
        code: str,
        language: str,
        constructions: list[str],
        run_compiler: bool = True,
        run_linter: bool = True,
        run_pattern: bool = True,
    ) -> list[ErrorMessage]:
        errors: list[ErrorMessage] = []
        has_compiler_errors = False

        if run_compiler:
            compiler_output = self._factory.create_compiler(language, code)
            compiler_errors = ErrorMessage.from_output(compiler_output, "COMPILER")
            errors.extend(compiler_errors)
            has_compiler_errors = bool(compiler_errors)

        if run_linter and not has_compiler_errors:
            linter_output = self._factory.create_linter(language, code)
            errors.extend(ErrorMessage.from_output(linter_output, "LINTER"))

        if run_pattern and constructions:
            pattern_output = self._factory.create_pattern(
                code, language, constructions
            )
            errors.extend(ErrorMessage.from_output(pattern_output, "CONSTRUCTION"))

        return errors
