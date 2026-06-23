"""Persistence for task_curriculum_link."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from domain.learning.curriculum.task_link import TaskCurriculumLink
from domain.learning.curriculum.task_link_exceptions import TaskCurriculumLinkValidationError
from infrastructure.db.models.task.task_curriculum_link import TaskCurriculumLinkModel


class TaskCurriculumLinkRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def list_by_task_id(self, task_id: int) -> list[TaskCurriculumLink]:
        return self.list_by_task_ids([task_id]).get(task_id, [])

    def list_by_task_ids(self, task_ids: list[int]) -> dict[int, list[TaskCurriculumLink]]:
        if not task_ids:
            return {}
        unique_ids = list(dict.fromkeys(task_ids))
        rows = self._session.scalars(
            select(TaskCurriculumLinkModel)
            .where(TaskCurriculumLinkModel.task_id.in_(unique_ids))
            .order_by(
                TaskCurriculumLinkModel.task_id.asc(),
                TaskCurriculumLinkModel.is_primary.desc(),
                TaskCurriculumLinkModel.created_at.asc(),
                TaskCurriculumLinkModel.id.asc(),
            )
        ).all()
        grouped: dict[int, list[TaskCurriculumLink]] = {task_id: [] for task_id in unique_ids}
        for row in rows:
            grouped[row.task_id].append(_to_record(row))
        return grouped

    def get_by_id(self, link_id: int) -> TaskCurriculumLink | None:
        row = self._session.get(TaskCurriculumLinkModel, link_id)
        return _to_record(row) if row else None

    def get_by_task_and_pattern(
        self,
        task_id: int,
        exercise_pattern_id: str,
    ) -> TaskCurriculumLink | None:
        row = self._session.scalars(
            select(TaskCurriculumLinkModel).where(
                TaskCurriculumLinkModel.task_id == task_id,
                TaskCurriculumLinkModel.exercise_pattern_id == exercise_pattern_id,
            )
        ).first()
        return _to_record(row) if row else None

    def clear_primary_for_task(self, task_id: int, *, language: str | None = None) -> None:
        stmt = select(TaskCurriculumLinkModel).where(
            TaskCurriculumLinkModel.task_id == task_id,
            TaskCurriculumLinkModel.is_primary.is_(True),
        )
        if language is not None:
            stmt = stmt.where(TaskCurriculumLinkModel.language == language.strip().lower())
        rows = self._session.scalars(stmt).all()
        for row in rows:
            row.is_primary = False
        if rows:
            self._session.flush()

    def create(
        self,
        *,
        task_id: int,
        language: str,
        learning_concept_id: str,
        technical_concept_id: str,
        exercise_pattern_id: str,
        action: str,
        is_primary: bool = False,
    ) -> TaskCurriculumLink:
        if is_primary:
            self.clear_primary_for_task(task_id, language=language)
        row = TaskCurriculumLinkModel(
            task_id=task_id,
            language=language,
            learning_concept_id=learning_concept_id,
            technical_concept_id=technical_concept_id,
            exercise_pattern_id=exercise_pattern_id,
            action=action,
            is_primary=is_primary,
        )
        self._session.add(row)
        try:
            self._session.flush()
        except IntegrityError as exc:
            self._session.rollback()
            raise TaskCurriculumLinkValidationError(
                "Task already linked to this exercise pattern or primary link conflict"
            ) from exc
        self._session.refresh(row)
        return _to_record(row)

    def update(
        self,
        link_id: int,
        *,
        is_primary: bool | None = None,
        technical_concept_id: str | None = None,
        exercise_pattern_id: str | None = None,
        language: str | None = None,
        learning_concept_id: str | None = None,
        action: str | None = None,
    ) -> TaskCurriculumLink | None:
        row = self._session.get(TaskCurriculumLinkModel, link_id)
        if row is None:
            return None
        if is_primary is True:
            next_lang = language or row.language
            self.clear_primary_for_task(row.task_id, language=next_lang)
        if is_primary is not None:
            row.is_primary = is_primary
        if technical_concept_id is not None:
            row.technical_concept_id = technical_concept_id
        if exercise_pattern_id is not None:
            row.exercise_pattern_id = exercise_pattern_id
        if language is not None:
            row.language = language
        if learning_concept_id is not None:
            row.learning_concept_id = learning_concept_id
        if action is not None:
            row.action = action
        try:
            self._session.flush()
        except IntegrityError as exc:
            self._session.rollback()
            raise TaskCurriculumLinkValidationError(
                "Task already linked to this exercise pattern or primary link conflict"
            ) from exc
        self._session.refresh(row)
        return _to_record(row)

    def delete(self, link_id: int) -> bool:
        row = self._session.get(TaskCurriculumLinkModel, link_id)
        if row is None:
            return False
        self._session.delete(row)
        self._session.flush()
        return True


def _to_record(row: TaskCurriculumLinkModel) -> TaskCurriculumLink:
    return TaskCurriculumLink(
        id=row.id,
        task_id=row.task_id,
        language=row.language,
        learning_concept_id=row.learning_concept_id,
        technical_concept_id=row.technical_concept_id,
        exercise_pattern_id=row.exercise_pattern_id,
        action=row.action,
        is_primary=row.is_primary,
        created_at=row.created_at,
    )
