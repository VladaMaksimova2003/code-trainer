from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class UserAccountSettings:
    user_id: int
    name: str
    email: str
    about: str | None
    roles: tuple[str, ...]


@dataclass(frozen=True)
class UserLearningPreferences:
    user_id: int
    preferred_languages: tuple[str, ...] = ()
    preferred_difficulty: str = "beginner"
    preferred_topics: tuple[str, ...] = ()
    study_place: str | None = None
    study_group: str | None = None


@dataclass(frozen=True)
class TeacherProfileSettings:
    user_id: int
    full_name: str
    bio: str | None
    specialization: str | None
    supported_languages: tuple[str, ...] = ()
    is_public: bool = True


@dataclass(frozen=True)
class TeacherOverviewItem:
    id: int
    name: str
    extra: str | None = None


@dataclass(frozen=True)
class TeacherOverview:
    groups: list[TeacherOverviewItem] = field(default_factory=list)
    assignment_sets: list[TeacherOverviewItem] = field(default_factory=list)
