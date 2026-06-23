from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError as PyJwtInvalidTokenError

from shared.interfaces.services.auth import ITokenProvider
from shared.exceptions import InvalidTokenError, TokenExpiredError
from domain.policies.rbac.role import Role


class JwtTokenProvider(ITokenProvider):
    def __init__(
        self,
        secret_key: str,
        issuer: str,
        audience: str,
        algorithm: str = "HS256",
        access_token_ttl_minutes: int = 15,
        refresh_token_ttl_days: int = 30,
    ) -> None:
        self._secret_key = secret_key
        self._issuer = issuer
        self._audience = audience
        self._algorithm = algorithm
        self._access_token_ttl_minutes = access_token_ttl_minutes
        self._refresh_token_ttl_days = refresh_token_ttl_days

    def create_access_token(self, user_id: int, role: Role) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": str(user_id),
            "role": str(role),
            "type": "access",
            "iat": now,
            "nbf": now,
            "exp": now + timedelta(minutes=self._access_token_ttl_minutes),
            "iss": self._issuer,
            "aud": self._audience,
        }
        return self._encode(payload)

    def create_refresh_token(self, user_id: int, role: Role) -> tuple[str, str, datetime]:
        now = datetime.now(UTC)
        jti = str(uuid4())
        expires_at = now + timedelta(days=self._refresh_token_ttl_days)
        payload = {
            "sub": str(user_id),
            "role": str(role),
            "type": "refresh",
            "jti": jti,
            "iat": now,
            "nbf": now,
            "exp": expires_at,
            "iss": self._issuer,
            "aud": self._audience,
        }
        token = self._encode(payload)
        return token, jti, expires_at

    def decode_access_token(self, token: str) -> dict:
        payload = self._decode(token)
        self._assert_token_type(payload, expected_type="access")
        return payload

    def decode_refresh_token(self, token: str) -> dict:
        payload = self._decode(token)
        self._assert_token_type(payload, expected_type="refresh")
        return payload

    def _encode(self, payload: dict) -> str:
        return jwt.encode(payload, self._secret_key, algorithm=self._algorithm)

    def _decode(self, token: str) -> dict:
        try:
            return jwt.decode(
                token,
                self._secret_key,
                algorithms=[self._algorithm],
                issuer=self._issuer,
                audience=self._audience,
            )
        except ExpiredSignatureError as exc:
            raise TokenExpiredError("Token is expired.") from exc
        except PyJwtInvalidTokenError as exc:
            raise InvalidTokenError("Token is invalid.") from exc

    @staticmethod
    def _assert_token_type(payload: dict, expected_type: str) -> None:
        actual_type = payload.get("type")
        if actual_type != expected_type:
            raise InvalidTokenError(
                f"Invalid token type: expected '{expected_type}', got '{actual_type}'."
            )
