from abc import ABC, abstractmethod


class CheckerFactoryInterface(ABC):
    @abstractmethod
    def create_linter(self, language: str, code: str) -> list[str]:
        pass

    @abstractmethod
    def create_compiler(self, language: str, code: str) -> list[str]:
        pass

    @abstractmethod
    def create_pattern(
        self, code: str, language: str, expected_patterns: list[str]
    ) -> list[str]:
        pass
