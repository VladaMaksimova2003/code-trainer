from passlib.context import CryptContext

from shared.interfaces.services.auth import IPasswordHasher


class PasswordHasherService(IPasswordHasher):
    def __init__(self) -> None:
        # bcrypt is widely supported and suitable for production password hashing.
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, raw_password: str) -> str:
        return self._pwd_context.hash(raw_password)

    def verify(self, raw_password: str, password_hash: str) -> bool:
        return self._pwd_context.verify(raw_password, password_hash)
