"""User API — request schemas."""
from pydantic import BaseModel, Field


class UpdateAccountSettingsRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=64)
    email: str | None = Field(default=None, max_length=64)
    about: str | None = Field(default=None, max_length=2000)
    email_verification_code: str | None = Field(default=None, min_length=6, max_length=6)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8, max_length=128)


class UpdateLearningPreferencesRequest(BaseModel):
    preferred_languages: list[str] | None = None
    preferred_difficulty: str | None = None
    preferred_topics: list[str] | None = None
    study_place: str | None = Field(default=None, max_length=255)
    study_group: str | None = Field(default=None, max_length=128)


class UpdateTeacherSettingsRequest(BaseModel):
    full_name: str | None = Field(default=None, max_length=256)
    bio: str | None = Field(default=None, max_length=4000)
    specialization: str | None = Field(default=None, max_length=256)
    supported_languages: list[str] | None = None
    is_public: bool | None = None
