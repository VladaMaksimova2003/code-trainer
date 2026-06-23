from urllib.parse import urlencode

from application.auth.oauth.types import OAuthTokenResponse, OAuthUserProfile
from infrastructure.external.oauth.http import get_json, post_form
from shared.config import OAuthSettings
from shared.exceptions import AuthError

_GOOGLE_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
_GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
_GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def build_google_authorize_url(
    settings: OAuthSettings,
    *,
    state: str,
    code_challenge: str,
) -> str:
    params = {
        "response_type": "code",
        "client_id": settings.google_client_id,
        "redirect_uri": settings.callback_url("google"),
        "state": state,
        "scope": "openid email profile",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "access_type": "online",
        "prompt": "select_account",
    }
    return f"{_GOOGLE_AUTHORIZE_URL}?{urlencode(params)}"


async def exchange_google_code(
    settings: OAuthSettings,
    *,
    code: str,
    code_verifier: str,
) -> OAuthTokenResponse:
    payload = await post_form(
        _GOOGLE_TOKEN_URL,
        {
            "grant_type": "authorization_code",
            "code": code,
            "code_verifier": code_verifier,
            "redirect_uri": settings.callback_url("google"),
            "client_id": settings.google_client_id,
            "client_secret": settings.google_client_secret,
        },
    )
    access_token = str(payload.get("access_token") or "").strip()
    if not access_token:
        raise AuthError("Google did not return an access token.")
    refresh_token = str(payload.get("refresh_token") or "").strip() or None
    return OAuthTokenResponse(access_token=access_token, refresh_token=refresh_token)


async def fetch_google_profile(access_token: str) -> OAuthUserProfile:
    payload = await get_json(
        _GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    provider_user_id = str(payload.get("sub") or "").strip()
    if not provider_user_id:
        raise AuthError("Google profile is missing user id.")

    name = str(payload.get("name") or "").strip() or "Пользователь Google"
    email = str(payload.get("email") or "").strip() or None
    avatar_url = str(payload.get("picture") or "").strip() or None

    return OAuthUserProfile(
        provider_user_id=provider_user_id,
        name=name[:64],
        email=email,
        avatar_url=avatar_url,
    )
