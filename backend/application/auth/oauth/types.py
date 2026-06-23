from dataclasses import dataclass


@dataclass(frozen=True)
class OAuthTokenResponse:
    access_token: str
    refresh_token: str | None = None


@dataclass(frozen=True)
class OAuthUserProfile:
    provider_user_id: str
    name: str
    email: str | None = None
    avatar_url: str | None = None
