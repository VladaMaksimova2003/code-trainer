"""Link existing tasks to curriculum v2 metadata (no mastery/review)."""

from __future__ import annotations

from sqlalchemy.orm import Session

from application.curriculum.core.curriculum_service import CurriculumService
from domain.learning.curriculum.exceptions import CurriculumNotFoundError
from domain.learning.curriculum.task_link import TaskCurriculumLink
from domain.learning.curriculum.task_link_exceptions import (
    TaskCurriculumLinkNotFoundError,
    TaskCurriculumLinkValidationError,
)
from infrastructure.db.models.task.task import Task
from infrastructure.repositories.curriculum.task_curriculum_link_repository import (
    TaskCurriculumLinkRepository,
)
from shared.exceptions import TaskNotFoundError


def validate_task_curriculum_link_metadata(
    language: str,
    technical_concept_id: str,
    exercise_pattern_id: str,
) -> dict[str, str]:
    """Stateless validation against YAML curriculum (no DB)."""
    lang = language.strip().lower()
    try:
        bundle = CurriculumService(lang).get_bundle()
    except CurriculumNotFoundError as exc:
        raise TaskCurriculumLinkValidationError(str(exc)) from exc

    tc = bundle.technical_concept_by_id(technical_concept_id)
    if tc is None:
        raise TaskCurriculumLinkValidationError(
            f"Unknown technical concept: {technical_concept_id}"
        )

    pattern = bundle.pattern_by_id(exercise_pattern_id)
    if pattern is None:
        raise TaskCurriculumLinkValidationError(
            f"Unknown exercise pattern: {exercise_pattern_id}"
        )

    mask = bundle.action_masks.get(technical_concept_id)
    if mask is None:
        raise TaskCurriculumLinkValidationError(
            f"No action mask for technical concept: {technical_concept_id}"
        )

    action = pattern.action
    if action in mask.disabled_actions:
        raise TaskCurriculumLinkValidationError(
            f"Action {action} is disabled for technical concept {technical_concept_id}"
        )
    if action not in mask.active_actions():
        raise TaskCurriculumLinkValidationError(
            f"Action {action} is not active for technical concept {technical_concept_id}"
        )

    allowed_patterns = set(mask.patterns_for_action(action))
    if exercise_pattern_id not in allowed_patterns:
        raise TaskCurriculumLinkValidationError(
            f"Pattern {exercise_pattern_id} is not allowed for "
            f"{technical_concept_id}/{action}"
        )

    return {
        "language": lang,
        "learning_concept_id": tc.learning_concept_id,
        "technical_concept_id": technical_concept_id,
        "exercise_pattern_id": exercise_pattern_id,
        "action": action,
    }


class TaskCurriculumLinkService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repo = TaskCurriculumLinkRepository(session)

    def _ensure_task_exists(self, task_id: int) -> None:
        task = self._session.get(Task, task_id)
        if task is None or task.is_delete:
            raise TaskNotFoundError(f"Task {task_id} not found")

    def validate_task_curriculum_link(
        self,
        language: str,
        technical_concept_id: str,
        exercise_pattern_id: str,
    ) -> dict[str, str]:
        return validate_task_curriculum_link_metadata(
            language,
            technical_concept_id,
            exercise_pattern_id,
        )

    def link_task_to_curriculum(
        self,
        task_id: int,
        language: str,
        technical_concept_id: str,
        exercise_pattern_id: str,
        *,
        is_primary: bool = False,
    ) -> TaskCurriculumLink:
        self._ensure_task_exists(task_id)
        meta = self.validate_task_curriculum_link(
            language,
            technical_concept_id,
            exercise_pattern_id,
        )
        existing = self._repo.get_by_task_and_pattern(task_id, exercise_pattern_id)
        if existing is not None:
            raise TaskCurriculumLinkValidationError(
                f"Task {task_id} is already linked to pattern {exercise_pattern_id}"
            )
        return self._repo.create(
            task_id=task_id,
            language=meta["language"],
            learning_concept_id=meta["learning_concept_id"],
            technical_concept_id=meta["technical_concept_id"],
            exercise_pattern_id=meta["exercise_pattern_id"],
            action=meta["action"],
            is_primary=is_primary,
        )

    def get_task_curriculum_links(self, task_id: int) -> list[TaskCurriculumLink]:
        self._ensure_task_exists(task_id)
        return self._repo.list_by_task_id(task_id)

    def get_task_curriculum_metadata(self, task_id: int) -> dict:
        self._ensure_task_exists(task_id)
        links = self._repo.list_by_task_id(task_id)
        primary = next((link for link in links if link.is_primary), None)
        return {
            "task_id": task_id,
            "has_curriculum_link": bool(links),
            "primary_link": _link_to_dict(primary) if primary else None,
            "links": [_link_to_dict(link) for link in links],
        }

    def get_primary_links_by_task_ids(
        self,
        task_ids: list[int],
        *,
        language: str | None = None,
    ) -> dict[int, dict | None]:
        if not task_ids:
            return {}
        links_by_task = self._repo.list_by_task_ids(task_ids)
        result: dict[int, dict | None] = {}
        lang_filter = str(language).strip().lower() if language else None
        for task_id, links in links_by_task.items():
            primary = _select_primary_link(links, lang_filter)
            result[task_id] = _link_to_dict(primary) if primary else None
        return result

    def get_primary_links_index(
        self,
        task_ids: list[int],
        *,
        languages: tuple[str, ...] = ("pascal", "python", "cpp", "csharp", "java"),
    ) -> dict[tuple[int, str], dict]:
        """One DB round-trip for all language tracks."""
        if not task_ids:
            return {}
        links_by_task = self._repo.list_by_task_ids(task_ids)
        result: dict[tuple[int, str], dict] = {}
        for task_id, links in links_by_task.items():
            for lang in languages:
                primary = _select_primary_link(links, lang)
                if primary:
                    result[(task_id, lang)] = _link_to_dict(primary)
        return result

    def get_primary_link_for_task(
        self,
        task_id: int,
        *,
        language: str | None = None,
    ) -> dict | None:
        return self.get_primary_links_by_task_ids([task_id], language=language).get(task_id)

    def primary_link_for_existing_task(
        self,
        task_id: int,
        *,
        language: str | None = None,
    ) -> tuple[bool, dict | None]:
        """Curriculum links for a task row already loaded (skips existence check)."""
        links = self._repo.list_by_task_id(task_id)
        if not links:
            return False, None
        lang_filter = language.strip().lower() if language else None
        primary = _select_primary_link(links, lang_filter)
        return True, _link_to_dict(primary) if primary else None

    def update_link(
        self,
        task_id: int,
        link_id: int,
        *,
        is_primary: bool | None = None,
        technical_concept_id: str | None = None,
        exercise_pattern_id: str | None = None,
        language: str | None = None,
    ) -> TaskCurriculumLink:
        self._ensure_task_exists(task_id)
        existing = self._repo.get_by_id(link_id)
        if existing is None or existing.task_id != task_id:
            raise TaskCurriculumLinkNotFoundError(
                f"Curriculum link {link_id} not found for task {task_id}"
            )

        next_language = language or existing.language
        next_tc = technical_concept_id or existing.technical_concept_id
        next_pattern = exercise_pattern_id or existing.exercise_pattern_id

        if (
            technical_concept_id is not None
            or exercise_pattern_id is not None
            or language is not None
        ):
            meta = self.validate_task_curriculum_link(
                next_language,
                next_tc,
                next_pattern,
            )
            if exercise_pattern_id and exercise_pattern_id != existing.exercise_pattern_id:
                duplicate = self._repo.get_by_task_and_pattern(task_id, next_pattern)
                if duplicate is not None and duplicate.id != link_id:
                    raise TaskCurriculumLinkValidationError(
                        f"Task {task_id} is already linked to pattern {next_pattern}"
                    )
            updated = self._repo.update(
                link_id,
                is_primary=is_primary,
                technical_concept_id=meta["technical_concept_id"],
                exercise_pattern_id=meta["exercise_pattern_id"],
                language=meta["language"],
                learning_concept_id=meta["learning_concept_id"],
                action=meta["action"],
            )
        else:
            updated = self._repo.update(link_id, is_primary=is_primary)

        if updated is None:
            raise TaskCurriculumLinkNotFoundError(
                f"Curriculum link {link_id} not found for task {task_id}"
            )
        return updated

    def delete_link(self, task_id: int, link_id: int) -> None:
        self._ensure_task_exists(task_id)
        existing = self._repo.get_by_id(link_id)
        if existing is None or existing.task_id != task_id:
            raise TaskCurriculumLinkNotFoundError(
                f"Curriculum link {link_id} not found for task {task_id}"
            )
        self._repo.delete(link_id)


def _select_primary_link(
    links: list[TaskCurriculumLink],
    language: str | None,
) -> TaskCurriculumLink | None:
    if not links:
        return None
    lang_filter = str(language).strip().lower() if language else None
    if lang_filter:
        same_lang = [link for link in links if link.language == lang_filter]
        if same_lang:
            return next((link for link in same_lang if link.is_primary), same_lang[0])
    return next((link for link in links if link.is_primary), links[0])


def _link_to_dict(link: TaskCurriculumLink) -> dict:
    return {
        "id": link.id,
        "task_id": link.task_id,
        "language": link.language,
        "learning_concept_id": link.learning_concept_id,
        "technical_concept_id": link.technical_concept_id,
        "exercise_pattern_id": link.exercise_pattern_id,
        "action": link.action,
        "is_primary": link.is_primary,
        "created_at": link.created_at.isoformat() if link.created_at else None,
    }
