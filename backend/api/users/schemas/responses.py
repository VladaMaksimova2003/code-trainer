"""User API — response schemas."""
from pydantic import BaseModel


class AvatarResponse(BaseModel):
    initial: str
    color: str


class AccountSettingsResponse(BaseModel):
    user_id: int
    name: str
    email: str
    avatar: AvatarResponse
    about: str | None = None
    roles: list[str]


class LearningPreferencesResponse(BaseModel):
    preferred_languages: list[str]
    preferred_difficulty: str
    preferred_topics: list[str]
    study_place: str | None = None
    study_group: str | None = None


class TeacherSettingsResponse(BaseModel):
    full_name: str
    bio: str | None = None
    specialization: str | None = None
    supported_languages: list[str]
    is_public: bool
    avatar: AvatarResponse


class TeacherOverviewItemResponse(BaseModel):
    id: int
    name: str
    extra: str | None = None


class TeacherOverviewResponse(BaseModel):
    groups: list[TeacherOverviewItemResponse]
    assignment_sets: list[TeacherOverviewItemResponse]
