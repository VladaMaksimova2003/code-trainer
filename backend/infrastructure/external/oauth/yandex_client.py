from urllib.parse import urlencode

from application.auth.oauth.types import OAuthTokenResponse, OAuthUserProfile
from infrastructure.external.oauth.http import get_json, post_form
from shared.config import OAuthSettings
from shared.exceptions import AuthError

_YANDEX_AUTHORIZE_URL = "https://oauth.yandex.ru/authorize"
_YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"
_YANDEX_USERINFO_URL = "https://login.yandex.ru/info"


def build_yandex_authorize_url(
    settings: OAuthSettings,
    *,
    state: str,
    code_challenge: str,
) -> str:
    params = {
        "response_type": "code",
        "client_id": settings.yandex_client_id,
        "redirect_uri": settings.callback_url("yandex"),
        "state": state,
        "scope": "login:email login:info",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    return f"{_YANDEX_AUTHORIZE_URL}?{urlencode(params)}"


async def exchange_yandex_code(
    settings: OAuthSettings,
    *,
    code: str,
    code_verifier: str,
) -> OAuthTokenResponse:
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "code_verifier": code_verifier,
        "redirect_uri": settings.callback_url("yandex"),
        "client_id": settings.yandex_client_id,
    }
    if settings.yandex_client_secret.strip():
        data["client_secret"] = settings.yandex_client_secret
    payload = await post_form(_YANDEX_TOKEN_URL, data)
    access_token = str(payload.get("access_token") or "").strip()
    if not access_token:
        raise AuthError("Yandex did not return an access token.")
    refresh_token = str(payload.get("refresh_token") or "").strip() or None
    return OAuthTokenResponse(access_token=access_token, refresh_token=refresh_token)


async def fetch_yandex_profile(access_token: str) -> OAuthUserProfile:
    payload = await get_json(
        f"{_YANDEX_USERINFO_URL}?format=json",
        headers={"Authorization": f"OAuth {access_token}"},
    )
    provider_user_id = str(payload.get("id") or payload.get("client_id") or "").strip()
    if not provider_user_id:
        raise AuthError("Yandex profile is missing user id.")

    first_name = str(payload.get("first_name") or "").strip()
    last_name = str(payload.get("last_name") or "").strip()
    display_name = str(payload.get("display_name") or "").strip()
    name = display_name or " ".join(part for part in (first_name, last_name) if part).strip()
    name = name or "Пользователь Яндекс"
    email = str(payload.get("default_email") or "").strip() or None
    avatar_url = None
    if isinstance(payload.get("default_avatar_id"), str) and payload["default_avatar_id"]:
        avatar_url = f"https://avatars.yandex.net/get-yapic/{payload['default_avatar_id']}/islands-200"

    return OAuthUserProfile(
        provider_user_id=provider_user_id,
        name=name[:64],
        email=email,
        avatar_url=avatar_url,
    )
