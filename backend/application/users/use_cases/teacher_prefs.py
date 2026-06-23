from __future__ import annotations

from shared.interfaces.repositories.users.user_settings import IUserSettingsRepository
from shared.interfaces.uow import IUnitOfWork
from application.users.dto import UpdateTeacherProfileCommand
from shared.enums import UserType
from shared.language import parse_language
from domain.entities.users.profile import TeacherOverview, TeacherProfileSettings
from shared.exceptions import TeacherProfileAccessError


def _normalize_languages(raw: list[str]) -> list[str]:
    result: list[str] = []
    for item in raw:
        value = str(item).strip().lower()
        if not value:
            continue
        try:
            parse_language(value)
        except ValueError:
            pass
        if value not in result:
            result.append(value)
    return result


class GetTeacherSettingsUseCase:
    def __init__(self, repo: IUserSettingsRepository, uow: IUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def execute(self, user_id: int, roles: frozenset[UserType]) -> TeacherProfileSettings:
        if UserType.TEACHER not in roles and UserType.ADMIN not in roles:
            raise TeacherProfileAccessError("Teacher role required")
        with self._uow():
            settings = self._repo.get_teacher_settings(user_id)
            if settings is None:
                raise TeacherProfileAccessError("User not found")
            return settings


class UpdateTeacherSettingsUseCase:
    def __init__(self, repo: IUserSettingsRepository, uow: IUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def execute(
        self,
        user_id: int,
        roles: frozenset[UserType],
        command: UpdateTeacherProfileCommand,
    ) -> TeacherProfileSettings:
        if UserType.TEACHER not in roles and UserType.ADMIN not in roles:
            raise TeacherProfileAccessError("Teacher role required")

        languages = None
        if command.supported_languages is not None:
            languages = _normalize_languages(command.supported_languages)

        with self._uow(autocommit=True):
            return self._repo.update_teacher_settings(
                user_id,
                full_name=command.full_name.strip() if command.full_name else None,
                bio=command.bio,
                specialization=command.specialization,
                supported_languages=languages,
                is_public=command.is_public,
            )


class GetTeacherOverviewUseCase:
    def __init__(self, repo: IUserSettingsRepository, uow: IUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def execute(self, user_id: int, roles: frozenset[UserType]) -> TeacherOverview:
        if UserType.TEACHER not in roles and UserType.ADMIN not in roles:
            raise TeacherProfileAccessError("Teacher role required")
        with self._uow():
            return self._repo.get_teacher_overview(user_id)
