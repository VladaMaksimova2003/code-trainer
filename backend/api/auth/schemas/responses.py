"""Auth API — response schemas."""
from pydantic import BaseModel

from api.users.schemas.responses import AvatarResponse


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int | None = None


class CurrentUserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    roles: list[str]
    avatar: AvatarResponse


class UserCreatedResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
