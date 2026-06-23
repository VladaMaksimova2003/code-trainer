from application.auth.services.email_verification import EmailVerificationService


class VerifyEmailCodeUseCase:
    def __init__(self, verification_service: EmailVerificationService) -> None:
        self._verification_service = verification_service

    def execute(self, *, email: str, purpose: str, code: str) -> None:
        self._verification_service.check_code(email, purpose=purpose, code=code)
