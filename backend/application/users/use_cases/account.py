from __future__ import annotations

import re

from application.auth.services.email_verification import email_verification_service
from shared.interfaces.repositories.users.user_settings import IUserSettingsRepository
from shared.interfaces.uow import IUnitOfWork
from application.users.dto import UpdateAccountCommand
from domain.entities.users.profile import UserAccountSettings
from shared.exceptions import EmailAlreadyInUseError, ProfileError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class GetAccountSettingsUseCase:
    def __init__(self, repo: IUserSettingsRepository, uow: IUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def execute(self, user_id: int) -> UserAccountSettings:
        with self._uow():
            account = self._repo.get_account(user_id)
            if account is None:
                raise ProfileError("User not found")
            return account


class UpdateAccountSettingsUseCase:
    def __init__(self, repo: IUserSettingsRepository, uow: IUnitOfWork) -> None:
        self._repo = repo
        self._uow = uow

    def execute(self, user_id: int, command: UpdateAccountCommand) -> UserAccountSettings:
        with self._uow(autocommit=True):
            account = self._repo.get_account(user_id)
            if account is None:
                raise ProfileError("User not found")

            if command.name is not None and not command.name.strip():
                raise ProfileError("Name cannot be empty")
            if command.email is not None:
                email = command.email.strip().lower()
                if not _EMAIL_RE.match(email):
                    raise ProfileError("Invalid email address")
                if self._repo.email_taken_by_other(email, user_id):
                    raise EmailAlreadyInUseError("Email is already in use")
                if email != (account.email or "").strip().lower():
                    if not command.email_verification_code:
                        raise ProfileError("Email verification code is required")
                    email_verification_service.verify_and_consume(
                        email,
                        purpose="change_email",
                        code=command.email_verification_code,
                    )
            return self._repo.update_account(
                user_id,
                name=command.name.strip() if command.name else None,
                email=command.email.strip().lower() if command.email else None,
                about=command.about,
            )
