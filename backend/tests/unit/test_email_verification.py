import pytest

from application.auth.services.email_verification import EmailVerificationService
from shared.exceptions import EmailVerificationError


class _FakeRedis:
    def __init__(self) -> None:
        self._store: dict[str, str] = {}

    def setex(self, key: str, ttl: int, value: str) -> None:
        self._store[key] = value

    def get(self, key: str) -> str | None:
        return self._store.get(key)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)


@pytest.fixture
def verification_service() -> EmailVerificationService:
    return EmailVerificationService(client=_FakeRedis())


def test_issue_and_verify_code(verification_service: EmailVerificationService):
    email = "student@example.com"
    code = verification_service.issue_code(email, purpose="register")
    assert len(code) == 6
    verification_service.check_code(email, purpose="register", code=code)


def test_verify_and_consume_removes_code(verification_service: EmailVerificationService):
    email = "student@example.com"
    code = verification_service.issue_code(email, purpose="reset_password")
    verification_service.verify_and_consume(email, purpose="reset_password", code=code)
    with pytest.raises(EmailVerificationError):
        verification_service.check_code(email, purpose="reset_password", code=code)


def test_invalid_code_rejected(verification_service: EmailVerificationService):
    email = "student@example.com"
    verification_service.issue_code(email, purpose="register")
    with pytest.raises(EmailVerificationError):
        verification_service.check_code(email, purpose="register", code="000000")


def test_normalize_email(verification_service: EmailVerificationService):
    assert verification_service.normalize_email("  User@Example.COM ") == "user@example.com"
