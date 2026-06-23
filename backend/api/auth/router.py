from fastapi import APIRouter, Depends, HTTPException, Request, status

from api.dependencies.auth import (
    current_user_roles_response,
    get_auth_rate_limiter,
    get_current_user,
    get_email_send_rate_limiter,
    get_forgot_password_use_case,
    get_login_use_case,
    get_logout_use_case,
    get_register_use_case,
    get_refresh_tokens_use_case,
    get_reset_password_use_case,
    get_send_email_verification_code_use_case,
    get_verify_email_code_use_case,
    to_login_command,
    to_register_command,
    to_refresh_command,
)
from api.auth.schemas import (
    AuthResponse,
    CurrentUserResponse,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    RefreshRequest,
    ResetPasswordRequest,
    SendEmailVerificationCodeRequest,
    VerifyEmailCodeRequest,
)
from application.users.services.avatar_service import AvatarService
from application.auth.dto import CurrentUserResult
from api.users.schemas import AvatarResponse
from application.auth.use_cases.sessions.login import LoginUseCase
from application.auth.use_cases.sessions.logout import LogoutUseCase
from application.auth.use_cases.sessions.refresh_tokens import RefreshTokensUseCase
from application.auth.use_cases.sessions.register import RegisterUseCase
from application.auth.use_cases.email_verification.send_code import SendEmailVerificationCodeUseCase
from application.auth.use_cases.password.forgot_password import ForgotPasswordUseCase
from application.auth.use_cases.password.reset_password import ResetPasswordUseCase
from application.auth.use_cases.email_verification.verify_code import VerifyEmailCodeUseCase
from infrastructure.security.auth_rate_limiter import AuthRateLimitError, AuthRateLimiter
from infrastructure.security.email_send_rate_limiter import EmailSendRateLimitError, EmailSendRateLimiter
from shared.exceptions import AuthError, EmailDeliveryError, EmailVerificationError, UserAlreadyExistsError
from api.auth.oauth_router import oauth_router

router = APIRouter()
router.include_router(oauth_router)


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    http_request: Request,
    use_case: LoginUseCase = Depends(get_login_use_case),
    rate_limiter: AuthRateLimiter = Depends(get_auth_rate_limiter),
) -> AuthResponse:
    client_ip = _client_ip(http_request)
    try:
        rate_limiter.check_allowed(request.email, client_ip)
        result = use_case.execute(to_login_command(request.email, request.password))
        rate_limiter.reset(request.email, client_ip)
        return AuthResponse(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            token_type=result.token_type,
            expires_in=result.expires_in,
        )
    except AuthRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
            headers={"Retry-After": str(exc.retry_after_seconds)},
        ) from exc
    except AuthError as exc:
        rate_limiter.register_failure(request.email, client_ip)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/email/send-code", status_code=status.HTTP_204_NO_CONTENT)
async def send_email_verification_code(
    request: SendEmailVerificationCodeRequest,
    http_request: Request,
    use_case: SendEmailVerificationCodeUseCase = Depends(get_send_email_verification_code_use_case),
    rate_limiter: EmailSendRateLimiter = Depends(get_email_send_rate_limiter),
) -> None:
    purpose = (request.purpose or "").strip().lower()
    if purpose not in {"register", "change_email"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid purpose.")
    try:
        rate_limiter.check_and_register(
            email=request.email,
            purpose=purpose,
            ip_address=_client_ip(http_request),
        )
        use_case.execute(email=request.email, purpose=purpose, exclude_user_id=None)
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


@router.post("/email/verify-code", status_code=status.HTTP_204_NO_CONTENT)
async def verify_email_code(
    request: VerifyEmailCodeRequest,
    use_case: VerifyEmailCodeUseCase = Depends(get_verify_email_code_use_case),
) -> None:
    purpose = (request.purpose or "").strip().lower()
    if purpose not in {"register", "change_email"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid purpose.")
    try:
        use_case.execute(email=request.email, purpose=purpose, code=request.code)
    except EmailVerificationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/forgot-password", status_code=status.HTTP_204_NO_CONTENT)
async def forgot_password(
    request: ForgotPasswordRequest,
    http_request: Request,
    use_case: ForgotPasswordUseCase = Depends(get_forgot_password_use_case),
    rate_limiter: EmailSendRateLimiter = Depends(get_email_send_rate_limiter),
) -> None:
    try:
        rate_limiter.check_and_register(
            email=request.email,
            purpose="reset_password",
            ip_address=_client_ip(http_request),
        )
        use_case.execute(email=request.email)
    except EmailSendRateLimitError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Слишком много запросов кода. Попробуйте позже.",
            headers={"Retry-After": str(exc.retry_after_seconds)},
        ) from exc
    except EmailVerificationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except EmailDeliveryError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    request: ResetPasswordRequest,
    use_case: ResetPasswordUseCase = Depends(get_reset_password_use_case),
) -> None:
    try:
        use_case.execute(
            email=request.email,
            code=request.code,
            new_password=request.new_password,
        )
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    use_case: RegisterUseCase = Depends(get_register_use_case),
) -> AuthResponse:
    try:
        tokens = use_case.execute(
            to_register_command(
                request.name,
                request.email,
                request.password,
                request.email_verification_code,
            )
        )
        return AuthResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type="bearer",
        )
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except EmailVerificationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/refresh", response_model=AuthResponse)
async def refresh_tokens(
    request: RefreshRequest,
    use_case: RefreshTokensUseCase = Depends(get_refresh_tokens_use_case),
) -> AuthResponse:
    try:
        tokens = use_case.execute(to_refresh_command(request.refresh_token))
        return AuthResponse(
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            token_type="bearer",
        )
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: RefreshRequest,
    use_case: LogoutUseCase = Depends(get_logout_use_case),
) -> None:
    try:
        use_case.execute(to_refresh_command(request.refresh_token))
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.get("/me", response_model=CurrentUserResponse)
async def me(
    current_user: CurrentUserResult = Depends(get_current_user),
) -> CurrentUserResponse:
    primary = (
        current_user.role.value
        if hasattr(current_user.role, "value")
        else str(current_user.role)
    )
    avatar = AvatarService.get_avatar(current_user.id, current_user.name)
    return CurrentUserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=primary,
        roles=current_user_roles_response(current_user),
        avatar=AvatarResponse(initial=avatar.initial, color=avatar.color),
    )
