from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UpdateAccountCommand:
    name: str | None = None
    email: str | None = None
    about: str | None = None
    email_verification_code: str | None = None


@dataclass(frozen=True)
class ChangePasswordCommand:
    current_password: str
    new_password: str


@dataclass(frozen=True)
class UpdateLearningPreferencesCommand:
    preferred_languages: list[str] | None = None
    preferred_difficulty: str | None = None
    preferred_topics: list[str] | None = None
    study_place: str | None = None
    study_group: str | None = None


@dataclass(frozen=True)
class UpdateTeacherProfileCommand:
    full_name: str | None = None
    bio: str | None = None
    specialization: str | None = None
    supported_languages: list[str] | None = None
    is_public: bool | None = None
