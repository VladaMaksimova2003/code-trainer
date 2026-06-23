from shared.interfaces.repositories.users.auth_session import IAuthSessionRepository
from shared.interfaces.repositories.users.user import IUserRepository
from shared.interfaces.services.auth import ITokenProvider
from shared.interfaces.uow import IUnitOfWork
from application.auth.dto import RefreshTokenCommand
from domain.entities.users.auth import AuthSession
from shared.exceptions import InvalidTokenError, SessionRevokedError, TokenExpiredError
from domain.policies.rbac.rbac import primary_role
from domain.value_objects.auth import TokenPair


class RefreshTokensUseCase:
    def __init__(
        self,
        user_repository: IUserRepository,
        auth_session_repository: IAuthSessionRepository,
        token_provider: ITokenProvider,
        uow: IUnitOfWork,
    ) -> None:
        self._user_repository = user_repository
        self._auth_session_repository = auth_session_repository
        self._token_provider = token_provider
        self._uow = uow

    def execute(self, command: RefreshTokenCommand) -> TokenPair:
        with self._uow(autocommit=True):
            payload = self._token_provider.decode_refresh_token(command.refresh_token)

            if payload.get("type") != "refresh":
                raise InvalidTokenError("Token type must be refresh.")

            jti = payload.get("jti")
            if not isinstance(jti, str) or not jti:
                raise InvalidTokenError("Refresh token does not contain jti.")

            session = self._auth_session_repository.get_by_jti_hash(jti)
            if session is None:
                raise InvalidTokenError("Auth session not found.")

            if session.is_revoked:
                raise SessionRevokedError("Auth session is revoked.")
            if session.is_expired:
                raise TokenExpiredError("Refresh session is expired.")

            user = self._user_repository.get(session.user_id)

            main_role = primary_role(user.roles)
            access_token = self._token_provider.create_access_token(
                user_id=user.id, role=main_role
            )
            refresh_token, new_jti, refresh_expires_at = (
                self._token_provider.create_refresh_token(
                    user_id=user.id, role=main_role
                )
            )

            new_session = AuthSession(
                id=None,
                user_id=user.id,
                refresh_token_jti_hash=new_jti,
                expires_at=refresh_expires_at,
                rotated_from_id=session.id,
                user_agent=session.user_agent,
                ip_address=session.ip_address,
            )
            self._auth_session_repository.create(new_session)
            self._auth_session_repository.revoke(session.id)

            return TokenPair(
                access_token=access_token,
                refresh_token=refresh_token,
            )
