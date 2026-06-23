from shared.interfaces.repositories.users.user import IUserRepository
from shared.interfaces.services.auth import IPasswordHasher
from shared.interfaces.uow import IUnitOfWork
from application.auth.dto import RegisterCommand
from shared.exceptions import UserAlreadyExistsError
from shared.enums import UserType
from domain.entities.users.user import User


class CreateAdminUseCase:
    """Admin creates a new account with student + admin roles."""

    def __init__(
        self,
        user_repository: IUserRepository[User],
        password_hasher: IPasswordHasher,
        uow: IUnitOfWork,
    ) -> None:
        self._user_repository = user_repository
        self._password_hasher = password_hasher
        self._uow = uow

    def execute(self, command: RegisterCommand) -> User:
        with self._uow(autocommit=True):
            existing_user = self._user_repository.get_by_email(command.email)
            if existing_user is not None:
                raise UserAlreadyExistsError("User with this email already exists.")

            password_hash = self._password_hasher.hash(command.password)
            user = User(
                id=None,
                name=command.name,
                email=command.email,
                password=password_hash,
                roles=frozenset({UserType.STUDENT, UserType.ADMIN}),
            )
            return self._user_repository.create(user)
