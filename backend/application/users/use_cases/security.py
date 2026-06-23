from __future__ import annotations

from shared.interfaces.repositories.users.user_settings import IUserSettingsRepository
from shared.interfaces.services.auth import IPasswordHasher
from shared.interfaces.uow import IUnitOfWork
from application.users.dto import ChangePasswordCommand
from shared.exceptions import InvalidPasswordError, ProfileError

_MIN_PASSWORD_LEN = 8


class ChangePasswordUseCase:
    def __init__(
        self,
        repo: IUserSettingsRepository,
        password_hasher: IPasswordHasher,
        uow: IUnitOfWork,
    ) -> None:
        self._repo = repo
        self._password_hasher = password_hasher
        self._uow = uow

    def execute(self, user_id: int, command: ChangePasswordCommand) -> None:
        if len(command.new_password) < _MIN_PASSWORD_LEN:
            raise ProfileError(
                f"New password must be at least {_MIN_PASSWORD_LEN} characters"
            )
        with self._uow(autocommit=True):
            stored = self._repo.get_password_hash(user_id)
            if stored is None:
                raise ProfileError("User not found")
            if not self._password_hasher.verify(command.current_password, stored):
                raise InvalidPasswordError("Current password is incorrect")
            self._repo.update_password(
                user_id, self._password_hasher.hash(command.new_password)
            )
