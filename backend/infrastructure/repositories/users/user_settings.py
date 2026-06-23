from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from shared.interfaces.repositories.users.user_settings import IUserSettingsRepository
from domain.policies.rbac.rbac import roles_to_strings
from domain.entities.users.profile import (
    TeacherOverview,
    TeacherOverviewItem,
    TeacherProfileSettings,
    UserAccountSettings,
    UserLearningPreferences,
)
from infrastructure.db.models.task.collection import Collection
from infrastructure.db.models.learning.group import Group
from infrastructure.db.models.user.teacher_profile import TeacherProfile
from infrastructure.db.models.user import User as UserModel
from infrastructure.db.models.user.user_preferences import UserPreferences
from application.users.services.study_identity import normalize_study_field
from infrastructure.repositories.users.user_role import SqlAlchemyUserRoleRepository


class SqlAlchemyUserSettingsRepository(IUserSettingsRepository):
    def __init__(self, session: Session) -> None:
        self._session = session
        self._roles = SqlAlchemyUserRoleRepository(session)

    def _get_user(self, user_id: int) -> UserModel | None:
        return self._session.get(UserModel, user_id)

    def get_account(self, user_id: int) -> UserAccountSettings | None:
        user = self._get_user(user_id)
        if user is None:
            return None
        roles = self._roles.get_roles_for_user(user_id)
        return UserAccountSettings(
            user_id=user.id,
            name=user.name,
            email=user.email,
            about=user.about,
            roles=tuple(roles_to_strings(roles)),
        )

    def update_account(
        self,
        user_id: int,
        *,
        name: str | None = None,
        email: str | None = None,
        about: str | None = None,
    ) -> UserAccountSettings:
        user = self._get_user(user_id)
        if user is None:
            raise ValueError("User not found")
        if name is not None:
            user.name = name.strip()
        if email is not None:
            user.email = email.strip().lower()
        if about is not None:
            user.about = about.strip() or None
        self._session.flush()
        result = self.get_account(user_id)
        assert result is not None
        return result

    def email_taken_by_other(self, email: str, user_id: int) -> bool:
        stmt = select(UserModel.id).where(
            UserModel.email == email.strip().lower(),
            UserModel.id != user_id,
        )
        return self._session.execute(stmt).scalar_one_or_none() is not None

    def get_password_hash(self, user_id: int) -> str | None:
        user = self._get_user(user_id)
        return user.password if user else None

    def update_password(self, user_id: int, password_hash: str) -> None:
        user = self._get_user(user_id)
        if user is None:
            raise ValueError("User not found")
        user.password = password_hash
        self._session.flush()

    def _ensure_preferences(self, user_id: int) -> UserPreferences:
        prefs = (
            self._session.query(UserPreferences)
            .filter(UserPreferences.user_id == user_id)
            .first()
        )
        if prefs is None:
            prefs = UserPreferences(user_id=user_id)
            self._session.add(prefs)
            self._session.flush()
        return prefs

    def get_learning_preferences(self, user_id: int) -> UserLearningPreferences:
        prefs = self._ensure_preferences(user_id)
        return UserLearningPreferences(
            user_id=user_id,
            preferred_languages=tuple(prefs.preferred_languages or []),
            preferred_difficulty=prefs.preferred_difficulty,
            preferred_topics=tuple(prefs.preferred_topics or []),
            study_place=normalize_study_field(getattr(prefs, "study_place", None), max_len=255),
            study_group=normalize_study_field(getattr(prefs, "study_group", None), max_len=128),
        )

    def update_learning_preferences(
        self,
        user_id: int,
        *,
        preferred_languages: list[str] | None = None,
        preferred_difficulty: str | None = None,
        preferred_topics: list[str] | None = None,
        study_place: str | None = None,
        study_group: str | None = None,
    ) -> UserLearningPreferences:
        prefs = self._ensure_preferences(user_id)
        if preferred_languages is not None:
            prefs.preferred_languages = preferred_languages
        if preferred_difficulty is not None:
            prefs.preferred_difficulty = preferred_difficulty
        if preferred_topics is not None:
            prefs.preferred_topics = preferred_topics
        if study_place is not None:
            prefs.study_place = normalize_study_field(study_place, max_len=255)
        if study_group is not None:
            prefs.study_group = normalize_study_field(study_group, max_len=128)
        self._session.flush()
        return self.get_learning_preferences(user_id)

    def _ensure_teacher_profile(self, user: UserModel) -> TeacherProfile:
        profile = (
            self._session.query(TeacherProfile)
            .filter(TeacherProfile.user_id == user.id)
            .first()
        )
        if profile is None:
            profile = TeacherProfile(
                user_id=user.id,
                full_name=user.name,
                languages=[],
            )
            self._session.add(profile)
            self._session.flush()
        return profile

    def get_teacher_settings(self, user_id: int) -> TeacherProfileSettings | None:
        user = self._get_user(user_id)
        if user is None:
            return None
        profile = (
            self._session.query(TeacherProfile)
            .filter(TeacherProfile.user_id == user_id)
            .first()
        )
        if profile is None:
            return TeacherProfileSettings(
                user_id=user_id,
                full_name=user.name,
                bio=None,
                specialization=None,
                supported_languages=(),
                is_public=True,
                avatar_url=user.avatar_url,
            )
        return TeacherProfileSettings(
            user_id=user_id,
            full_name=profile.full_name or user.name,
            bio=profile.bio,
            specialization=profile.specialization,
            supported_languages=tuple(profile.languages or []),
            is_public=bool(profile.is_public),
            avatar_url=profile.avatar_url or user.avatar_url,
        )

    def update_teacher_settings(
        self,
        user_id: int,
        *,
        full_name: str | None = None,
        bio: str | None = None,
        specialization: str | None = None,
        supported_languages: list[str] | None = None,
        is_public: bool | None = None,
    ) -> TeacherProfileSettings:
        user = self._get_user(user_id)
        if user is None:
            raise ValueError("User not found")
        profile = self._ensure_teacher_profile(user)
        if full_name is not None:
            profile.full_name = full_name.strip()
        if bio is not None:
            profile.bio = bio.strip() or None
        if specialization is not None:
            profile.specialization = specialization.strip() or None
        if supported_languages is not None:
            profile.languages = supported_languages
        if is_public is not None:
            profile.is_public = is_public
        self._session.flush()
        result = self.get_teacher_settings(user_id)
        assert result is not None
        return result

    def get_teacher_overview(self, user_id: int) -> TeacherOverview:
        groups = (
            self._session.query(Group)
            .filter(Group.teacher_id == user_id)
            .order_by(Group.id.desc())
            .limit(20)
            .all()
        )
        sets = (
            self._session.query(Collection)
            .filter(Collection.teacher_id == user_id, Collection.is_archived.is_(False))
            .order_by(Collection.id.desc())
            .limit(20)
            .all()
        )
        return TeacherOverview(
            groups=[
                TeacherOverviewItem(id=g.id, name=g.name) for g in groups
            ],
            assignment_sets=[
                TeacherOverviewItem(
                    id=s.id,
                    name=s.name,
                    extra=(
                        s.visibility.value
                        if hasattr(s.visibility, "value")
                        else str(s.visibility)
                        if s.visibility is not None
                        else None
                    ),
                )
                for s in sets
            ],
        )
