from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TeacherSearchFilters:
    name: str | None = None
    language: str | None = None
    specialization: str | None = None


@dataclass
class TeacherSearchResult:
    user_id: int
    full_name: str
    bio: str | None
    languages: list[str]
    specialization: str | None
    assignment_count: int
    assignment_set_count: int


class ITeacherSearchRepository(ABC):
    @abstractmethod
    def search(self, filters: TeacherSearchFilters, limit: int = 50) -> list[TeacherSearchResult]:
        pass

    @abstractmethod
    def get_public_profile(self, teacher_id: int) -> TeacherSearchResult | None:
        pass
