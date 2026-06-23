from shared.interfaces.repositories.learning.assignment_set import IAssignmentSetRepository
from shared.interfaces.repositories.learning.teacher_search import (
    ITeacherSearchRepository,
    TeacherSearchFilters,
    TeacherSearchResult,
)
from application.tasks.services.content_access_service import ContentAccessService
from shared.enums import AssignmentSetVisibility


class SearchTeachersUseCase:
    def __init__(self, search: ITeacherSearchRepository) -> None:
        self._search = search

    def execute(
        self,
        name: str | None = None,
        language: str | None = None,
        specialization: str | None = None,
        limit: int = 50,
    ) -> list[TeacherSearchResult]:
        return self._search.search(
            TeacherSearchFilters(name=name, language=language, specialization=specialization),
            limit=limit,
        )


class GetTeacherPublicProfileUseCase:
    def __init__(
        self,
        search: ITeacherSearchRepository,
        sets: IAssignmentSetRepository,
    ) -> None:
        self._search = search
        self._sets = sets

    def execute(self, teacher_id: int) -> tuple[TeacherSearchResult | None, list]:
        profile = self._search.get_public_profile(teacher_id)
        if profile is None:
            return None, []
        public_sets = [
            s
            for s in self._sets.list_discoverable_public()
            if s.teacher_id == teacher_id
        ]
        return profile, public_sets
