"""Settings — account CRUD and security."""
from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.dependencies.auth import (
    get_current_user,
    get_email_send_rate_limiter,
    get_logout_use_case,
    get_send_email_verification_code_use_case,
    to_refresh_command,
)
from api.dependencies.settings import (
    get_account_settings_uc,
    get_change_password_uc,
    get_logout_all_uc,
    get_update_account_uc,
)
from api.auth.schemas import RefreshRequest
from api.users.schemas.requests import (
    ChangePasswordRequest,
    UpdateAccountSettingsRequest,
)
from api.users.schemas.responses import AccountSettingsResponse, AvatarResponse
from application.users.services.avatar_service import AvatarService
from application.auth.dto import CurrentUserResult
from application.auth.use_cases.email_verification.send_code import SendEmailVerificationCodeUseCase
from application.auth.use_cases.sessions.logout import LogoutUseCase
from application.auth.use_cases.sessions.logout_all_sessions import LogoutAllSessionsUseCase
from application.users.use_cases.account import GetAccountSettingsUseCase, UpdateAccountSettingsUseCase
from application.users.dto import ChangePasswordCommand, UpdateAccountCommand
from application.users.use_cases.security import ChangePasswordUseCase
from shared.exceptions import AuthError, EmailAlreadyInUseError, EmailDeliveryError, EmailVerificationError, InvalidPasswordError, ProfileError, UserAlreadyExistsError
from infrastructure.security.email_send_rate_limiter import EmailSendRateLimitError, EmailSendRateLimiter

router = APIRouter()


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    return request.client.host if request.client else "unknown"


def _account_response(data) -> AccountSettingsResponse:
    avatar = AvatarService.get_avatar(data.user_id, data.name)
    return AccountSettingsResponse(
        user_id=data.user_id,
        name=data.name,
        email=data.email,
        avatar=AvatarResponse(initial=avatar.initial, color=avatar.color),
        about=data.about,
        roles=list(data.roles),
    )


@router.get("/account", response_model=AccountSettingsResponse)
def get_account(
    current: CurrentUserResult = Depends(get_current_user),
    use_case: GetAccountSettingsUseCase = Depends(get_account_settings_uc),
):
    return _account_response(use_case.execute(current.id))


@router.patch("/account", response_model=AccountSettingsResponse)
def update_account(
    body: UpdateAccountSettingsRequest,
    current: CurrentUserResult = Depends(get_current_user),
    use_case: UpdateAccountSettingsUseCase = Depends(get_update_account_uc),
):
    try:
        result = use_case.execute(
            current.id,
            UpdateAccountCommand(
                name=body.name,
                email=body.email,
                about=body.about,
                email_verification_code=body.email_verification_code,
            ),
        )
        return _account_response(result)
    except EmailAlreadyInUseError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except ProfileError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/email/send-code", status_code=status.HTTP_204_NO_CONTENT)
def send_change_email_code(
    body: UpdateAccountSettingsRequest,
    http_request: Request,
    current: CurrentUserResult = Depends(get_current_user),
    use_case: SendEmailVerificationCodeUseCase = Depends(get_send_email_verification_code_use_case),
    rate_limiter: EmailSendRateLimiter = Depends(get_email_send_rate_limiter),
) -> None:
    if not body.email or not body.email.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required.")
    try:
        rate_limiter.check_and_register(
            email=body.email,
            purpose="change_email",
            ip_address=_client_ip(http_request),
        )
        use_case.execute(
            email=body.email,
            purpose="change_email",
            exclude_user_id=current.id,
        )
    except EmailSendRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Слишком много запросов кода. Попробуйте позже.",
            headers={"Retry-After": str(exc.retry_after_seconds)},
        ) from exc
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except EmailVerificationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except EmailDeliveryError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    body: ChangePasswordRequest,
    current: CurrentUserResult = Depends(get_current_user),
    use_case: ChangePasswordUseCase = Depends(get_change_password_uc),
):
    try:
        use_case.execute(
            current.id,
            ChangePasswordCommand(
                current_password=body.current_password,
                new_password=body.new_password,
            ),
        )
    except InvalidPasswordError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ProfileError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_session(
    request: RefreshRequest,
    use_case: LogoutUseCase = Depends(get_logout_use_case),
) -> None:
    try:
        use_case.execute(to_refresh_command(request.refresh_token))
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/logout-all", status_code=status.HTTP_204_NO_CONTENT)
def logout_all_sessions(
    current: CurrentUserResult = Depends(get_current_user),
    use_case: LogoutAllSessionsUseCase = Depends(get_logout_all_uc),
) -> None:
    use_case.execute(current.id)
