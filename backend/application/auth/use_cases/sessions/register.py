from application.auth.services.email_verification import email_verification_service
from shared.interfaces.repositories.users.auth_session import IAuthSessionRepository
from shared.interfaces.repositories.users.user import IUserRepository
from shared.interfaces.services.auth import IPasswordHasher, ITokenProvider
from shared.interfaces.uow import IUnitOfWork
from application.auth.dto import RegisterCommand
from application.auth.services.token_issuer import issue_token_pair
from shared.exceptions import AuthError, EmailVerificationError, UserAlreadyExistsError
from domain.value_objects.auth import TokenPair
from shared.enums import UserType
from domain.entities.users.user import User


class RegisterUseCase:
    def __init__(
        self,
        user_repository: IUserRepository[User],
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

    def execute(self, command: RegisterCommand) -> TokenPair:
        if not command.email_verification_code:
            raise EmailVerificationError("Email verification code is required.")
        with self._uow(autocommit=True):
            email_verification_service.verify_and_consume(
                command.email,
                purpose="register",
                code=command.email_verification_code,
            )
            existing_user = self._user_repository.get_by_email(command.email)
            if existing_user is not None:
                raise UserAlreadyExistsError("User with this email already exists.")

            password_hash = self._password_hasher.hash(command.password)
            user = User(
                id=None,
                name=command.name,
                email=command.email,
                password=password_hash,
                roles=frozenset({UserType.STUDENT}),
            )
            created_user = self._user_repository.create(user)
            return issue_token_pair(
                user=created_user,
                auth_session_repository=self._auth_session_repository,
                token_provider=self._token_provider,
            )
