from application.auth.services.email_verification import EmailVerificationService
from domain.entities.users.user import User
from infrastructure.services.email_sender import send_verification_code_email
from shared.interfaces.repositories.users.user import IUserRepository


class ForgotPasswordUseCase:
    def __init__(
        self,
        user_repository: IUserRepository[User],
        verification_service: EmailVerificationService,
    ) -> None:
        self._user_repository = user_repository
        self._verification_service = verification_service

    def execute(self, *, email: str) -> None:
        normalized = self._verification_service.validate_email_address(email)
        user = self._user_repository.get_by_email(normalized)
        if user is None or user.is_deleted:
            return

        code = self._verification_service.issue_code(normalized, purpose="reset_password")
        send_verification_code_email(to_email=normalized, code=code, purpose="reset_password")
