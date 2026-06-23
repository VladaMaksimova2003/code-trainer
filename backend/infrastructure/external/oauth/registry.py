from collections.abc import Awaitable, Callable

from application.auth.oauth.types import OAuthTokenResponse, OAuthUserProfile
from infrastructure.external.oauth import google_client, vk_client, yandex_client
from shared.config import OAuthSettings
from shared.exceptions import AuthError

OAuthProfileFetcher = Callable[[OAuthSettings, str], Awaitable[OAuthUserProfile]]
OAuthCodeExchanger = Callable[..., Awaitable[OAuthTokenResponse]]

_SUPPORTED_PROVIDERS = frozenset({"vk", "google", "yandex"})


def normalize_provider(provider: str) -> str:
    normalized = (provider or "").strip().lower()
    if normalized not in _SUPPORTED_PROVIDERS:
        raise AuthError("Unsupported OAuth provider.")
    return normalized


def build_authorize_url(
    provider: str,
    settings: OAuthSettings,
    *,
    state: str,
    code_challenge: str,
) -> str:
    normalized = normalize_provider(provider)
    if not settings.is_provider_configured(normalized):
        raise AuthError(f"OAuth provider '{normalized}' is not configured.")

    builders = {
        "vk": vk_client.build_vk_authorize_url,
        "google": google_client.build_google_authorize_url,
        "yandex": yandex_client.build_yandex_authorize_url,
    }
    return builders[normalized](settings, state=state, code_challenge=code_challenge)


async def exchange_code(
    provider: str,
    settings: OAuthSettings,
    *,
    code: str,
    code_verifier: str,
    device_id: str | None = None,
) -> OAuthTokenResponse:
    normalized = normalize_provider(provider)
    if normalized == "vk":
        return await vk_client.exchange_vk_code(
            settings,
            code=code,
            code_verifier=code_verifier,
            device_id=device_id,
        )
    if normalized == "google":
        return await google_client.exchange_google_code(
            settings,
            code=code,
            code_verifier=code_verifier,
        )
    return await yandex_client.exchange_yandex_code(
        settings,
        code=code,
        code_verifier=code_verifier,
    )


async def fetch_profile(
    provider: str,
    settings: OAuthSettings,
    access_token: str,
) -> OAuthUserProfile:
    normalized = normalize_provider(provider)
    if normalized == "vk":
        return await vk_client.fetch_vk_profile(settings, access_token)
    if normalized == "google":
        return await google_client.fetch_google_profile(access_token)
    return await yandex_client.fetch_yandex_profile(access_token)
