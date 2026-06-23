from abc import ABC, abstractmethod


class ExtractorServiceInterface(ABC):
    @abstractmethod
    def extract(self, code: str, language: str) -> list[str]:
        pass
