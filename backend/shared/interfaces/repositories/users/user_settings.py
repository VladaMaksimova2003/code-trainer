from abc import ABC, abstractmethod

from domain.entities.users.profile import (
    TeacherOverview,
    TeacherProfileSettings,
    UserAccountSettings,
    UserLearningPreferences,
)


class IUserSettingsRepository(ABC):
    @abstractmethod
    def get_account(self, user_id: int) -> UserAccountSettings | None:
        pass

    @abstractmethod
    def update_account(
        self,
        user_id: int,
        *,
        name: str | None = None,
        email: str | None = None,
        about: str | None = None,
    ) -> UserAccountSettings:
        pass

    @abstractmethod
    def email_taken_by_other(self, email: str, user_id: int) -> bool:
        pass

    @abstractmethod
    def get_password_hash(self, user_id: int) -> str | None:
        pass

    @abstractmethod
    def update_password(self, user_id: int, password_hash: str) -> None:
        pass

    @abstractmethod
    def get_learning_preferences(self, user_id: int) -> UserLearningPreferences:
        pass

    @abstractmethod
    def update_learning_preferences(
        self,
        user_id: int,
        *,
        preferred_languages: list[str] | None = None,
        preferred_difficulty: str | None = None,
        preferred_topics: list[str] | None = None,
        study_place: str | None = None,
        study_group: str | None = None,
    ) -> UserLearningPreferences:
        pass

    @abstractmethod
    def get_teacher_settings(self, user_id: int) -> TeacherProfileSettings | None:
        pass

    @abstractmethod
    def update_teacher_settings(
        self,
        user_id: int,
        *,
        full_name: str | None = None,
        bio: str | None = None,
        specialization: str | None = None,
        supported_languages: list[str] | None = None,
        is_public: bool | None = None,
    ) -> TeacherProfileSettings:
        pass

    @abstractmethod
    def get_teacher_overview(self, user_id: int) -> TeacherOverview:
        pass
