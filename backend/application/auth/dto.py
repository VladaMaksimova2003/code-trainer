from pydantic import BaseModel

from domain.policies.rbac.role import Role


class LoginCommand(BaseModel):
    email: str
    password: str


class RegisterCommand(BaseModel):
    name: str
    email: str
    password: str
    email_verification_code: str | None = None


class RefreshTokenCommand(BaseModel):
    refresh_token: str


class AuthResult(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int | None = None
    user_id: int
    role: Role


class CurrentUserResult(BaseModel):
    id: int
    name: str
    email: str
    role: Role
    roles: list[Role]
