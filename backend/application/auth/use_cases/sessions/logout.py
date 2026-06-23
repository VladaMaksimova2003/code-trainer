from shared.interfaces.repositories.users.auth_session import IAuthSessionRepository
from shared.interfaces.services.auth import ITokenProvider
from shared.interfaces.uow import IUnitOfWork
from application.auth.dto import RefreshTokenCommand
from shared.exceptions import InvalidTokenError


class LogoutUseCase:
    def __init__(
        self,
        auth_session_repository: IAuthSessionRepository,
        token_provider: ITokenProvider,
        uow: IUnitOfWork,
    ) -> None:
        self._auth_session_repository = auth_session_repository
        self._token_provider = token_provider
        self._uow = uow

    def execute(self, command: RefreshTokenCommand) -> None:
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

            self._auth_session_repository.revoke(session.id)
