from fastapi import Depends
from sqlalchemy.orm import Session

from api.dependencies.auth import SimpleUnitOfWork, get_current_user
from application.auth.dto import CurrentUserResult
from application.auth.use_cases.sessions.logout_all_sessions import LogoutAllSessionsUseCase
from application.users.use_cases.account import (
    GetAccountSettingsUseCase,
    UpdateAccountSettingsUseCase,
)
from application.users.use_cases.learning_prefs import (
    GetLearningPreferencesUseCase,
    UpdateLearningPreferencesUseCase,
)
from application.users.use_cases.security import ChangePasswordUseCase
from application.users.use_cases.teacher_prefs import (
    GetTeacherOverviewUseCase,
    GetTeacherSettingsUseCase,
    UpdateTeacherSettingsUseCase,
)
from infrastructure.db.session import get_db
from infrastructure.repositories.users.auth_session import (
    SqlAlchemyAuthSessionRepository,
)
from infrastructure.repositories.users.user_settings import (
    SqlAlchemyUserSettingsRepository,
)
from infrastructure.external.security.password_hasher import PasswordHasherService


def _settings_repo(db: Session = Depends(get_db)) -> SqlAlchemyUserSettingsRepository:
    return SqlAlchemyUserSettingsRepository(db)


def get_account_settings_uc(
    db: Session = Depends(get_db),
) -> GetAccountSettingsUseCase:
    return GetAccountSettingsUseCase(
        SqlAlchemyUserSettingsRepository(db), SimpleUnitOfWork(db)
    )


def get_update_account_uc(
    db: Session = Depends(get_db),
) -> UpdateAccountSettingsUseCase:
    return UpdateAccountSettingsUseCase(
        SqlAlchemyUserSettingsRepository(db), SimpleUnitOfWork(db)
    )


def get_change_password_uc(db: Session = Depends(get_db)) -> ChangePasswordUseCase:
    return ChangePasswordUseCase(
        SqlAlchemyUserSettingsRepository(db),
        PasswordHasherService(),
        SimpleUnitOfWork(db),
    )


def get_learning_preferences_uc(
    db: Session = Depends(get_db),
) -> GetLearningPreferencesUseCase:
    return GetLearningPreferencesUseCase(
        SqlAlchemyUserSettingsRepository(db), SimpleUnitOfWork(db)
    )


def get_update_learning_uc(
    db: Session = Depends(get_db),
) -> UpdateLearningPreferencesUseCase:
    return UpdateLearningPreferencesUseCase(
        SqlAlchemyUserSettingsRepository(db), SimpleUnitOfWork(db)
    )


def get_teacher_settings_uc(
    db: Session = Depends(get_db),
) -> GetTeacherSettingsUseCase:
    return GetTeacherSettingsUseCase(
        SqlAlchemyUserSettingsRepository(db), SimpleUnitOfWork(db)
    )


def get_update_teacher_uc(
    db: Session = Depends(get_db),
) -> UpdateTeacherSettingsUseCase:
    return UpdateTeacherSettingsUseCase(
        SqlAlchemyUserSettingsRepository(db), SimpleUnitOfWork(db)
    )


def get_teacher_overview_uc(
    db: Session = Depends(get_db),
) -> GetTeacherOverviewUseCase:
    return GetTeacherOverviewUseCase(
        SqlAlchemyUserSettingsRepository(db), SimpleUnitOfWork(db)
    )


def get_logout_all_uc(db: Session = Depends(get_db)) -> LogoutAllSessionsUseCase:
    return LogoutAllSessionsUseCase(
        SqlAlchemyAuthSessionRepository(db),
        SimpleUnitOfWork(db),
    )


def user_roles_set(user: CurrentUserResult = Depends(get_current_user)):
    from domain.policies.rbac.rbac import normalize_roles

    return normalize_roles(list(user.roles))
