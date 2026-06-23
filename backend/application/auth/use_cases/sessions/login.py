from shared.interfaces.repositories.users.auth_session import IAuthSessionRepository
from shared.interfaces.repositories.users.user import IUserRepository
from shared.interfaces.services.auth import IPasswordHasher, ITokenProvider
from shared.interfaces.uow import IUnitOfWork
from application.auth.dto import LoginCommand
from shared.exceptions import InvalidCredentialsError
from application.auth.services.token_issuer import issue_token_pair
from domain.value_objects.auth import TokenPair


class LoginUseCase:
    def __init__(
        self,
        user_repository: IUserRepository,
        auth_session_repository: IAuthSessionRepository,
        password_hasher: IPasswordHasher,
        token_provider: ITokenProvider,
        uow: IUnitOfWork,
    ) -> None:
        self._user_repository = user_repository
        self._auth_session_repository = auth_session_repository
        self._password_hasher = password_hasher
        self._token_provider = token_provider
        self._uow = uow

    def execute(self, command: LoginCommand) -> TokenPair:
        with self._uow(autocommit=True):
            user = self._user_repository.get_by_email(command.email)
            if user is None:
                raise InvalidCredentialsError("Invalid email or password.")

            if not self._password_hasher.verify(command.password, user.password):
                raise InvalidCredentialsError("Invalid email or password.")

            if not user.can_authenticate():
                raise InvalidCredentialsError("Account is disabled.")

            return issue_token_pair(
                user=user,
                auth_session_repository=self._auth_session_repository,
                token_provider=self._token_provider,
            )
