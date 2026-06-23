"""CheckerFactory — Docker via ExecutionCore (worker/API pipeline in worker only)."""
from __future__ import annotations

from shared.interfaces.services import CheckerFactoryInterface
from shared.config import CheckerSettings
from infrastructure.execution.execution_core import ExecutionCore
from infrastructure.execution.pattern.checker import PatternChecker
from infrastructure.execution.pattern.extractor import PatternExtractor


class CheckerFactory(CheckerFactoryInterface):
    def __init__(self, checker_settings: CheckerSettings) -> None:
        self.checker_settings = checker_settings
        self._core = ExecutionCore()

    def create_linter(self, language: str, code: str) -> list[str]:
        return self._core.lint(str(language).lower(), code)

    def create_compiler(self, language: str, code: str) -> list[str]:
        return self._core.compile_check(str(language).lower(), code)

    def create_pattern(
        self, code: str, language: str, expected_patterns: list[str]
    ) -> list[str]:
        extractor = PatternExtractor(self.checker_settings)
        checker = PatternChecker(extractor)
        return checker.check(code, str(language).lower(), expected_patterns)
