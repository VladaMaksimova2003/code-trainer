from application.auth.services.email_verification import EmailVerificationService
from domain.entities.users.user import User
from shared.exceptions import AuthError, EmailVerificationError
from shared.interfaces.repositories.users.auth_session import IAuthSessionRepository
from shared.interfaces.repositories.users.user import IUserRepository
from shared.interfaces.repositories.users.user_settings import IUserSettingsRepository
from shared.interfaces.services.auth import IPasswordHasher
from shared.interfaces.uow import IUnitOfWork

_MIN_PASSWORD_LEN = 8


class ResetPasswordUseCase:
    def __init__(
        self,
        user_repository: IUserRepository[User],
        settings_repository: IUserSettingsRepository,
        auth_session_repository: IAuthSessionRepository,
        verification_service: EmailVerificationService,
        password_hasher: IPasswordHasher,
        uow: IUnitOfWork,
    ) -> None:
        self._user_repository = user_repository
        self._settings_repository = settings_repository
        self._auth_session_repository = auth_session_repository
        self._verification_service = verification_service
        self._password_hasher = password_hasher
        self._uow = uow

    def execute(self, *, email: str, code: str, new_password: str) -> None:
        if len(new_password) < _MIN_PASSWORD_LEN:
            raise AuthError(f"Password must be at least {_MIN_PASSWORD_LEN} characters.")

        normalized = self._verification_service.normalize_email(email)
        try:
            self._verification_service.verify_and_consume(
                normalized,
                purpose="reset_password",
                code=code,
            )
        except EmailVerificationError as exc:
            raise AuthError(str(exc)) from exc

        user = self._user_repository.get_by_email(normalized)
        if user is None or user.is_deleted:
            raise AuthError("Invalid reset request.")

        with self._uow(autocommit=True):
            self._settings_repository.update_password(
                user.id,
                self._password_hasher.hash(new_password),
            )
            self._auth_session_repository.revoke_all_for_user(user.id)
