from __future__ import annotations

from shared.interfaces.repositories.users.user_settings import IUserSettingsRepository
from shared.interfaces.uow import IUnitOfWork
from application.users.dto import UpdateLearningPreferencesCommand
from shared.language import parse_language
from domain.entities.users.profile import UserLearningPreferences
from shared.enums import LearningTopic, PreferredDifficulty
from shared.exceptions import ProfileError
from application.users.services.study_identity import normalize_study_field


def _normalize_languages(raw: list[str]) -> list[str]:
    result: list[str] = []
    for item in raw:
        value = str(item).strip().lower()
        if not value:
            continue
        try:
            parse_language(value)
        except ValueError:
            raise ProfileError(f"Unsupported language: {item}") from None
        if value not in result:
            result.append(value)
    return result


class GetLearningPreferencesUseCase:
    def __init__(self, repo: IUserSettingsRepository, uow: IUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def execute(self, user_id: int) -> UserLearningPreferences:
        with self._uow():
            return self._repo.get_learning_preferences(user_id)


class UpdateLearningPreferencesUseCase:
    def __init__(self, repo: IUserSettingsRepository, uow: IUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def execute(
        self, user_id: int, command: UpdateLearningPreferencesCommand
    ) -> UserLearningPreferences:
        difficulty = None
        if command.preferred_difficulty is not None:
            difficulty = PreferredDifficulty.parse(command.preferred_difficulty).value

        topics = None
        if command.preferred_topics is not None:
            topics = [t.value for t in LearningTopic.parse_many(command.preferred_topics)]

        languages = None
        if command.preferred_languages is not None:
            languages = _normalize_languages(command.preferred_languages)

        study_place = None
        if command.study_place is not None:
            study_place = normalize_study_field(command.study_place, max_len=255)

        study_group = None
        if command.study_group is not None:
            study_group = normalize_study_field(command.study_group, max_len=128)

        with self._uow(autocommit=True):
            return self._repo.update_learning_preferences(
                user_id,
                preferred_languages=languages,
                preferred_difficulty=difficulty,
                preferred_topics=topics,
                study_place=study_place,
                study_group=study_group,
            )
