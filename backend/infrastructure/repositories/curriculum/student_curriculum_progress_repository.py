"""Persistence for student_curriculum_progress."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.db.models.learning.student_curriculum_progress import (
    StudentCurriculumProgressModel,
)


class StudentCurriculumProgressRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_user_and_task(
        self,
        user_id: int,
        task_id: int,
    ) -> StudentCurriculumProgressModel | None:
        """First progress row for user+task (legacy; prefer get_by_user_task_language)."""
        return self._session.scalars(
            select(StudentCurriculumProgressModel).where(
                StudentCurriculumProgressModel.user_id == user_id,
                StudentCurriculumProgressModel.task_id == task_id,
            )
        ).first()

    def get_by_user_task_language(
        self,
        user_id: int,
        task_id: int,
        language: str,
    ) -> StudentCurriculumProgressModel | None:
        lang = language.strip().lower()
        return self._session.scalars(
            select(StudentCurriculumProgressModel).where(
                StudentCurriculumProgressModel.user_id == user_id,
                StudentCurriculumProgressModel.task_id == task_id,
                StudentCurriculumProgressModel.language == lang,
            )
        ).first()

    def list_for_user_learning_concept(
        self,
        user_id: int,
        language: str,
        learning_concept_id: str,
    ) -> list[StudentCurriculumProgressModel]:
        return list(
            self._session.scalars(
                select(StudentCurriculumProgressModel).where(
                    StudentCurriculumProgressModel.user_id == user_id,
                    StudentCurriculumProgressModel.language == language,
                    StudentCurriculumProgressModel.learning_concept_id == learning_concept_id,
                )
            ).all()
        )

    def list_for_user_tasks(
        self,
        user_id: int,
        task_ids: list[int],
        *,
        language: str | None = None,
    ) -> list[StudentCurriculumProgressModel]:
        if not task_ids:
            return []
        query = select(StudentCurriculumProgressModel).where(
            StudentCurriculumProgressModel.user_id == user_id,
            StudentCurriculumProgressModel.task_id.in_(task_ids),
        )
        if language:
            query = query.where(
                StudentCurriculumProgressModel.language == language.strip().lower()
            )
        return list(self._session.scalars(query).all())

    def list_all_for_user(self, user_id: int) -> list[StudentCurriculumProgressModel]:
        return list(
            self._session.scalars(
                select(StudentCurriculumProgressModel).where(
                    StudentCurriculumProgressModel.user_id == user_id,
                )
            ).all()
        )
