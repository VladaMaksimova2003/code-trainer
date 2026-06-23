from application.auth.services.email_verification import EmailVerificationService
from infrastructure.services.email_sender import send_verification_code_email
from shared.interfaces.repositories.users.user import IUserRepository
from shared.exceptions import UserAlreadyExistsError
from domain.entities.users.user import User


class SendEmailVerificationCodeUseCase:
    def __init__(
        self,
        user_repository: IUserRepository[User],
        verification_service: EmailVerificationService,
    ) -> None:
        self._user_repository = user_repository
        self._verification_service = verification_service

    def execute(self, *, email: str, purpose: str, exclude_user_id: int | None = None) -> None:
        normalized = self._verification_service.validate_email_address(email)
        existing = self._user_repository.get_by_email(normalized)

        if purpose == "register":
            if existing is not None:
                raise UserAlreadyExistsError("User with this email already exists.")
        elif purpose == "change_email":
            if existing is not None and existing.id != exclude_user_id:
                raise UserAlreadyExistsError("Email is already in use.")
        else:
            raise ValueError("Unknown purpose")

        code = self._verification_service.issue_code(normalized, purpose=purpose)
        send_verification_code_email(to_email=normalized, code=code, purpose=purpose)
