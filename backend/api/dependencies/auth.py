from typing import Callable

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from application.auth.use_cases.teacher_role.approve_teacher_role_request import (
    ApproveTeacherRoleRequestUseCase,
)
from application.auth.services.email_verification import EmailVerificationService, email_verification_service
from application.auth.use_cases.password.forgot_password import ForgotPasswordUseCase
from application.auth.use_cases.password.reset_password import ResetPasswordUseCase
from application.auth.use_cases.email_verification.send_code import SendEmailVerificationCodeUseCase
from application.auth.use_cases.email_verification.verify_code import VerifyEmailCodeUseCase
from application.auth.use_cases.teacher_role.create_admin import CreateAdminUseCase
from application.auth.use_cases.teacher_role.create_teacher import CreateTeacherUseCase
from application.auth.dto import (
    CurrentUserResult,
    LoginCommand,
    RefreshTokenCommand,
    RegisterCommand,
)
from application.auth.use_cases.sessions.get_current_user import GetCurrentUserUseCase
from application.auth.use_cases.teacher_role.list_teacher_role_requests import (
    ListTeacherRoleRequestsUseCase,
)
from application.auth.use_cases.sessions.login import LoginUseCase
from application.auth.use_cases.sessions.logout import LogoutUseCase
from application.auth.use_cases.sessions.refresh_tokens import RefreshTokensUseCase
from application.auth.use_cases.oauth.complete_oauth_login import CompleteOAuthLoginUseCase
from application.auth.use_cases.sessions.register import RegisterUseCase
from application.auth.use_cases.teacher_role.reject_teacher_role_request import (
    RejectTeacherRoleRequestUseCase,
)
from application.auth.use_cases.teacher_role.request_teacher_role import RequestTeacherRoleUseCase
from shared.config import get_settings
from shared.exceptions import AuthError, InvalidTokenError
from domain.policies.rbac.rbac import normalize_role, roles_to_strings
from infrastructure.db.session import get_db
from infrastructure.repositories.users.auth_session import (
    SqlAlchemyAuthSessionRepository,
)
from infrastructure.repositories.admin.teacher_role_request import (
    SqlAlchemyTeacherRoleRequestRepository,
)
from infrastructure.security.auth_rate_limiter import AuthRateLimiter
from infrastructure.security.email_send_rate_limiter import EmailSendRateLimiter
from infrastructure.repositories.users.user_settings import SqlAlchemyUserSettingsRepository
from infrastructure.repositories.users.user import SqlAlchemyUsersRepository
from infrastructure.repositories.users.user_oauth import SqlAlchemyUserOAuthRepository
from infrastructure.repositories.users.user_role import SqlAlchemyUserRoleRepository
from infrastructure.external.security.jwt_token_provider import JwtTokenProvider
from infrastructure.external.security.password_hasher import PasswordHasherService


class SimpleUnitOfWork:
    def __init__(self, session: Session):
        self._session = session
        self._autocommit = False

    def __call__(self, autocommit: bool = False) -> "SimpleUnitOfWork":
        self._autocommit = autocommit
        return self

    def __enter__(self) -> "SimpleUnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self._session.rollback()
            return
        if self._autocommit:
            self._session.commit()


def _build_token_provider() -> JwtTokenProvider:
    settings = get_settings()
    return JwtTokenProvider(
        secret_key=settings.auth.secret_key,
        issuer=settings.auth.issuer,
        audience=settings.auth.audience,
        algorithm=settings.auth.algorithm,
        access_token_ttl_minutes=settings.auth.access_token_ttl_minutes,
        refresh_token_ttl_days=settings.auth.refresh_token_ttl_days,
    )


def get_login_use_case(db: Session = Depends(get_db)) -> LoginUseCase:
    return LoginUseCase(
        user_repository=SqlAlchemyUsersRepository(db),
        auth_session_repository=SqlAlchemyAuthSessionRepository(db),
        password_hasher=PasswordHasherService(),
        token_provider=_build_token_provider(),
        uow=SimpleUnitOfWork(db),
    )


def get_refresh_tokens_use_case(db: Session = Depends(get_db)) -> RefreshTokensUseCase:
    return RefreshTokensUseCase(
        user_repository=SqlAlchemyUsersRepository(db),
        auth_session_repository=SqlAlchemyAuthSessionRepository(db),
        token_provider=_build_token_provider(),
        uow=SimpleUnitOfWork(db),
    )


def get_complete_oauth_login_use_case(
    db: Session = Depends(get_db),
) -> CompleteOAuthLoginUseCase:
    settings = get_settings()
    return CompleteOAuthLoginUseCase(
        user_repository=SqlAlchemyUsersRepository(db),
        oauth_repository=SqlAlchemyUserOAuthRepository(db),
        auth_session_repository=SqlAlchemyAuthSessionRepository(db),
        password_hasher=PasswordHasherService(),
        token_provider=_build_token_provider(),
        oauth_settings=settings.oauth,
        auth_secret_key=settings.auth.secret_key,
        auth_algorithm=settings.auth.algorithm,
        uow=SimpleUnitOfWork(db),
    )


def get_register_use_case(db: Session = Depends(get_db)) -> RegisterUseCase:
    return RegisterUseCase(
        user_repository=SqlAlchemyUsersRepository(db),
        auth_session_repository=SqlAlchemyAuthSessionRepository(db),
        password_hasher=PasswordHasherService(),
        token_provider=_build_token_provider(),
        uow=SimpleUnitOfWork(db),
    )


def get_create_teacher_use_case(db: Session = Depends(get_db)) -> CreateTeacherUseCase:
    return CreateTeacherUseCase(
        user_repository=SqlAlchemyUsersRepository(db),
        password_hasher=PasswordHasherService(),
        uow=SimpleUnitOfWork(db),
    )


def get_create_admin_use_case(db: Session = Depends(get_db)) -> CreateAdminUseCase:
    return CreateAdminUseCase(
        user_repository=SqlAlchemyUsersRepository(db),
        password_hasher=PasswordHasherService(),
        uow=SimpleUnitOfWork(db),
    )


def get_send_email_verification_code_use_case(
    db: Session = Depends(get_db),
) -> SendEmailVerificationCodeUseCase:
    return SendEmailVerificationCodeUseCase(
        user_repository=SqlAlchemyUsersRepository(db),
        verification_service=email_verification_service,
    )


def get_verify_email_code_use_case() -> VerifyEmailCodeUseCase:
    return VerifyEmailCodeUseCase(verification_service=email_verification_service)


def get_forgot_password_use_case(
    db: Session = Depends(get_db),
) -> ForgotPasswordUseCase:
    return ForgotPasswordUseCase(
        user_repository=SqlAlchemyUsersRepository(db),
        verification_service=email_verification_service,
    )


def get_reset_password_use_case(db: Session = Depends(get_db)) -> ResetPasswordUseCase:
    return ResetPasswordUseCase(
        user_repository=SqlAlchemyUsersRepository(db),
        settings_repository=SqlAlchemyUserSettingsRepository(db),
        auth_session_repository=SqlAlchemyAuthSessionRepository(db),
        verification_service=email_verification_service,
        password_hasher=PasswordHasherService(),
        uow=SimpleUnitOfWork(db),
    )


def get_auth_rate_limiter() -> AuthRateLimiter:
    return AuthRateLimiter()


def get_email_send_rate_limiter() -> EmailSendRateLimiter:
    return EmailSendRateLimiter()


def get_logout_use_case(db: Session = Depends(get_db)) -> LogoutUseCase:
    return LogoutUseCase(
        auth_session_repository=SqlAlchemyAuthSessionRepository(db),
        token_provider=_build_token_provider(),
        uow=SimpleUnitOfWork(db),
    )


def get_current_user_use_case(db: Session = Depends(get_db)) -> GetCurrentUserUseCase:
    return GetCurrentUserUseCase(
        user_repository=SqlAlchemyUsersRepository(db),
        user_role_repository=SqlAlchemyUserRoleRepository(db),
    )


def get_request_teacher_role_use_case(
    db: Session = Depends(get_db),
) -> RequestTeacherRoleUseCase:
    return RequestTeacherRoleUseCase(
        user_repository=SqlAlchemyUsersRepository(db),
        user_role_repository=SqlAlchemyUserRoleRepository(db),
        request_repository=SqlAlchemyTeacherRoleRequestRepository(db),
        uow=SimpleUnitOfWork(db),
    )


def get_list_teacher_role_requests_use_case(
    db: Session = Depends(get_db),
) -> ListTeacherRoleRequestsUseCase:
    return ListTeacherRoleRequestsUseCase(
        request_repository=SqlAlchemyTeacherRoleRequestRepository(db),
    )


def get_approve_teacher_role_request_use_case(
    db: Session = Depends(get_db),
) -> ApproveTeacherRoleRequestUseCase:
    return ApproveTeacherRoleRequestUseCase(
        request_repository=SqlAlchemyTeacherRoleRequestRepository(db),
        user_role_repository=SqlAlchemyUserRoleRepository(db),
        uow=SimpleUnitOfWork(db),
    )


def get_reject_teacher_role_request_use_case(
    db: Session = Depends(get_db),
) -> RejectTeacherRoleRequestUseCase:
    return RejectTeacherRoleRequestUseCase(
        request_repository=SqlAlchemyTeacherRoleRequestRepository(db),
        uow=SimpleUnitOfWork(db),
    )


def _resolve_current_user(
    authorization: str | None,
    get_user_use_case: GetCurrentUserUseCase,
) -> CurrentUserResult | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "", 1).strip()
    token_provider = _build_token_provider()
    try:
        payload = token_provider.decode_access_token(token)
        user_id = int(payload["sub"])
        return get_user_use_case.execute(user_id=user_id)
    except (KeyError, ValueError, InvalidTokenError, AuthError):
        return None


def get_optional_current_user(
    authorization: str | None = Header(default=None),
    get_user_use_case: GetCurrentUserUseCase = Depends(get_current_user_use_case),
) -> CurrentUserResult | None:
    return _resolve_current_user(authorization, get_user_use_case)


def get_current_user(
    authorization: str | None = Header(default=None),
    get_user_use_case: GetCurrentUserUseCase = Depends(get_current_user_use_case),
) -> CurrentUserResult:
    user = _resolve_current_user(authorization, get_user_use_case)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid access token.",
        )
    return user


def to_login_command(email: str, password: str) -> LoginCommand:
    return LoginCommand(email=email, password=password)


def to_refresh_command(refresh_token: str) -> RefreshTokenCommand:
    return RefreshTokenCommand(refresh_token=refresh_token)


def to_register_command(
    name: str, email: str, password: str, email_verification_code: str
) -> RegisterCommand:
    return RegisterCommand(
        name=name,
        email=email,
        password=password,
        email_verification_code=email_verification_code,
    )


def to_admin_create_command(name: str, email: str, password: str) -> RegisterCommand:
    return RegisterCommand(name=name, email=email, password=password)


def current_user_roles_response(user: CurrentUserResult) -> list[str]:
    if user.roles:
        return [r.value if hasattr(r, "value") else str(r) for r in user.roles]
    return roles_to_strings(frozenset({normalize_role(user.role)}))
