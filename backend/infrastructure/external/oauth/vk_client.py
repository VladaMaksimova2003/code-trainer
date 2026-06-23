from urllib.parse import urlencode

from application.auth.oauth.types import OAuthTokenResponse, OAuthUserProfile
from infrastructure.external.oauth.http import post_form
from shared.config import OAuthSettings
from shared.exceptions import AuthError

_VK_AUTHORIZE_URL = "https://id.vk.ru/authorize"
_VK_TOKEN_URL = "https://id.vk.ru/oauth2/auth"
_VK_USER_INFO_URL = "https://id.vk.ru/oauth2/user_info"


def build_vk_authorize_url(
    settings: OAuthSettings,
    *,
    state: str,
    code_challenge: str,
) -> str:
    params = {
        "response_type": "code",
        "client_id": settings.vk_client_id,
        "redirect_uri": settings.callback_url("vk"),
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "scope": "email",
    }
    return f"{_VK_AUTHORIZE_URL}?{urlencode(params)}"


async def exchange_vk_code(
    settings: OAuthSettings,
    *,
    code: str,
    code_verifier: str,
    device_id: str | None,
) -> OAuthTokenResponse:
    if not device_id:
        raise AuthError("VK ID device_id is missing.")

    payload = await post_form(
        _VK_TOKEN_URL,
        {
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": code_verifier,
            "redirect_uri": settings.callback_url("vk"),
            "client_id": settings.vk_client_id,
            "device_id": device_id,
        },
    )
    access_token = str(payload.get("access_token") or "").strip()
    if not access_token:
        raise AuthError("VK ID did not return an access token.")
    refresh_token = str(payload.get("refresh_token") or "").strip() or None
    return OAuthTokenResponse(access_token=access_token, refresh_token=refresh_token)


async def fetch_vk_profile(settings: OAuthSettings, access_token: str) -> OAuthUserProfile:
    payload = await post_form(
        _VK_USER_INFO_URL,
        {
            "client_id": settings.vk_client_id,
            "access_token": access_token,
        },
    )
    user = payload.get("user")
    if not isinstance(user, dict):
        raise AuthError("VK ID profile response is invalid.")

    provider_user_id = str(user.get("user_id") or user.get("id") or "").strip()
    if not provider_user_id:
        raise AuthError("VK ID profile is missing user id.")

    first_name = str(user.get("first_name") or "").strip()
    last_name = str(user.get("last_name") or "").strip()
    name = " ".join(part for part in (first_name, last_name) if part).strip() or "Пользователь VK"
    email = str(user.get("email") or "").strip() or None
    avatar_url = str(user.get("avatar") or "").strip() or None

    return OAuthUserProfile(
        provider_user_id=provider_user_id,
        name=name[:64],
        email=email,
        avatar_url=avatar_url,
    )
