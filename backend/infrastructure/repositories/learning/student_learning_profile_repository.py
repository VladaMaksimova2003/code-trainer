"""Load/save StudentStructureProfile."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.learning.student_structure_profile import StudentStructureProfile
from infrastructure.db.models.learning.student_learning_profile import (
    StudentLearningProfileModel,
)


class StudentLearningProfileRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, user_id: int) -> StudentStructureProfile:
        row = self._session.scalars(
            select(StudentLearningProfileModel).where(
                StudentLearningProfileModel.user_id == user_id
            )
        ).first()
        if row is None:
            return StudentStructureProfile.empty(user_id)
        return StudentStructureProfile(
            user_id=user_id,
            structures=dict(row.structures_json or {}),
            weak_areas=list(row.weak_areas_json or []),
            failure_counts=dict(row.failure_counts_json or {}),
            learning_level=str(row.learning_level or "beginner"),
            consecutive_passes=int(row.consecutive_passes or 0),
        )

    def save(self, profile: StudentStructureProfile) -> StudentStructureProfile:
        row = self._session.scalars(
            select(StudentLearningProfileModel).where(
                StudentLearningProfileModel.user_id == profile.user_id
            )
        ).first()
        if row is None:
            row = StudentLearningProfileModel(user_id=profile.user_id)
            self._session.add(row)
        row.structures_json = dict(profile.structures)
        row.weak_areas_json = list(profile.weak_areas)
        row.failure_counts_json = dict(profile.failure_counts)
        row.learning_level = profile.learning_level
        row.consecutive_passes = profile.consecutive_passes
        self._session.flush()
        return profile
