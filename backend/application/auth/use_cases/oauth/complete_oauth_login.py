import secrets

from application.auth.oauth.state_store import consume_oauth_state
from application.auth.services.token_issuer import issue_token_pair
from domain.entities.users.user import User
from domain.value_objects.auth import TokenPair
from infrastructure.external.oauth.registry import exchange_code, fetch_profile, normalize_provider
from infrastructure.repositories.users.user_oauth import SqlAlchemyUserOAuthRepository
from shared.config import OAuthSettings
from shared.enums import UserType
from shared.exceptions import AuthError
from shared.interfaces.repositories.users.auth_session import IAuthSessionRepository
from shared.interfaces.repositories.users.user import IUserRepository
from shared.interfaces.services.auth import IPasswordHasher, ITokenProvider
from shared.interfaces.uow import IUnitOfWork


def _resolve_email(provider: str, provider_user_id: str, email: str | None) -> str:
    normalized_email = (email or "").strip().lower()
    if normalized_email:
        return normalized_email[:64]
    return f"{provider}_{provider_user_id}@oauth.code-trainer.local"


class CompleteOAuthLoginUseCase:
    def __init__(
        self,
        user_repository: IUserRepository[User],
        oauth_repository: SqlAlchemyUserOAuthRepository,
        auth_session_repository: IAuthSessionRepository,
        password_hasher: IPasswordHasher,
        token_provider: ITokenProvider,
        oauth_settings: OAuthSettings,
        uow: IUnitOfWork,
    ) -> None:
        self._user_repository = user_repository
        self._oauth_repository = oauth_repository
        self._auth_session_repository = auth_session_repository
        self._password_hasher = password_hasher
        self._token_provider = token_provider
        self._oauth_settings = oauth_settings
        self._uow = uow

    async def execute(
        self,
        *,
        provider: str,
        code: str,
        state: str,
        device_id: str | None = None,
    ) -> TokenPair:
        normalized_provider = normalize_provider(provider)
        if not self._oauth_settings.is_provider_configured(normalized_provider):
            raise AuthError(f"OAuth provider '{normalized_provider}' is not configured.")

        state_payload = consume_oauth_state(state)
        if state_payload["provider"] != normalized_provider:
            raise AuthError("OAuth provider mismatch.")

        tokens = await exchange_code(
            normalized_provider,
            self._oauth_settings,
            code=code,
            code_verifier=state_payload["code_verifier"],
            device_id=device_id,
        )
        profile = await fetch_profile(
            normalized_provider,
            self._oauth_settings,
            tokens.access_token,
        )

        with self._uow(autocommit=True):
            linked = self._oauth_repository.get_by_provider_account(
                normalized_provider,
                profile.provider_user_id,
            )
            if linked is not None:
                user = self._user_repository.get(linked.user_id)
                if user is None or not user.can_authenticate():
                    raise AuthError("Linked account is unavailable.")
                return issue_token_pair(
                    user=user,
                    auth_session_repository=self._auth_session_repository,
                    token_provider=self._token_provider,
                )

            resolved_email = _resolve_email(
                normalized_provider,
                profile.provider_user_id,
                profile.email,
            )
            user = self._user_repository.get_by_email(resolved_email)
            if user is None:
                password_hash = self._password_hasher.hash(secrets.token_urlsafe(32))
                user = User(
                    id=None,
                    name=profile.name,
                    email=resolved_email,
                    password=password_hash,
                    roles=frozenset({UserType.STUDENT}),
                )
                user = self._user_repository.create(user)
            elif not user.can_authenticate():
                raise AuthError("Account is disabled.")

            self._oauth_repository.create_link(
                user_id=user.id,
                provider=normalized_provider,
                provider_user_id=profile.provider_user_id,
                provider_email=profile.email,
            )
            return issue_token_pair(
                user=user,
                auth_session_repository=self._auth_session_repository,
                token_provider=self._token_provider,
            )
