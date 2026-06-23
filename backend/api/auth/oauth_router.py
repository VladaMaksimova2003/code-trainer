from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from starlette.requests import Request

from api.dependencies.auth import get_complete_oauth_login_use_case
from application.auth.oauth.pkce import generate_pkce_pair
from application.auth.oauth.state_token import create_oauth_state_token
from application.auth.use_cases.oauth.complete_oauth_login import CompleteOAuthLoginUseCase
from infrastructure.external.oauth.registry import build_authorize_url, normalize_provider
from shared.config import get_settings
from shared.exceptions import AuthError

oauth_router = APIRouter(prefix="/oauth", tags=["auth-oauth"])

_SUPPORTED_PROVIDERS = ("vk", "google", "yandex")


@oauth_router.get("/providers")
async def oauth_providers() -> dict[str, list[str]]:
    settings = get_settings().oauth
    configured = [
        provider
        for provider in _SUPPORTED_PROVIDERS
        if settings.is_provider_configured(provider)
    ]
    return {"providers": configured}


@oauth_router.get("/{provider}/start")
async def oauth_start(provider: str) -> RedirectResponse:
    settings = get_settings()
    oauth_settings = settings.oauth
    auth_settings = settings.auth

    try:
        normalized = normalize_provider(provider)
    except AuthError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    if not oauth_settings.is_provider_configured(normalized):
        redirect_url = oauth_settings.frontend_callback_url(
            error=f"Провайдер {normalized} не настроен на сервере.",
        )
        return RedirectResponse(url=redirect_url, status_code=302)

    code_verifier, code_challenge = generate_pkce_pair()
    state = create_oauth_state_token(
        provider=normalized,
        code_verifier=code_verifier,
        secret_key=auth_settings.secret_key,
        algorithm=auth_settings.algorithm,
    )
    authorize_url = build_authorize_url(
        normalized,
        oauth_settings,
        state=state,
        code_challenge=code_challenge,
    )
    return RedirectResponse(url=authorize_url, status_code=302)


@oauth_router.get("/{provider}/callback")
async def oauth_callback(
    request: Request,
    provider: str,
    use_case: CompleteOAuthLoginUseCase = Depends(get_complete_oauth_login_use_case),
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    device_id: str | None = Query(default=None),
    error: str | None = Query(default=None),
    error_description: str | None = Query(default=None),
) -> RedirectResponse:
    settings = get_settings()
    oauth_settings = settings.oauth

    if error:
        message = (error_description or error or "OAuth authorization failed.").strip()
        return RedirectResponse(
            url=oauth_settings.frontend_callback_url(error=message),
            status_code=302,
        )

    if not code or not state:
        return RedirectResponse(
            url=oauth_settings.frontend_callback_url(
                error="OAuth callback is missing code or state.",
            ),
            status_code=302,
        )

    try:
        token_pair = await use_case.execute(
            provider=provider,
            code=code,
            state=state,
            device_id=device_id or request.query_params.get("device_id"),
        )
    except AuthError as exc:
        return RedirectResponse(
            url=oauth_settings.frontend_callback_url(error=str(exc)),
            status_code=302,
        )

    return RedirectResponse(
        url=oauth_settings.frontend_callback_url(
            access_token=token_pair.access_token,
            refresh_token=token_pair.refresh_token,
        ),
        status_code=302,
    )
