"""Curriculum placement labels for admin assignment list."""

from __future__ import annotations

from dataclasses import dataclass

from application.curriculum.display.curriculum_labels import LANGUAGE_LABELS
from application.curriculum.shared.algo_v128_showcase import CHAPTER_ROUTE_SUFFIX
from application.tasks.services.catalog.task_teacher_list_meta import teacher_list_meta_for_row
from infrastructure.db.models.task import Task as TaskModel


@dataclass(frozen=True)
class AdminAssignmentPlacement:
    collection_title: str | None
    chapter_title: str | None
    chapter_key: str | None
    language: str | None
    chapter_slug: str | None
    teacher_name: str | None
    teacher_email: str | None


def _showcase_language(showcase: dict) -> str | None:
    lang = str(showcase.get("target_language") or "").strip().lower()
    if lang:
        return lang
    group = str(showcase.get("group") or "")
    for candidate in ("pascal", "python", "cpp", "csharp", "java"):
        if group.startswith(f"{candidate}_"):
            return candidate
    collection_id = str(showcase.get("collection_id") or "")
    for candidate in ("python", "pascal", "csharp", "cpp", "java"):
        if collection_id.startswith(f"{candidate}_"):
            return candidate
    return None


def admin_assignment_placement_for_row(
    row: TaskModel,
    *,
    chapter_titles: dict[str, str] | None,
    teacher_name: str | None,
    teacher_email: str | None,
) -> AdminAssignmentPlacement:
    meta = teacher_list_meta_for_row(row, chapter_titles=chapter_titles)
    examples = dict(row.code_examples or {})
    showcase_raw = examples.get("curriculum_showcase")
    showcase = dict(showcase_raw) if isinstance(showcase_raw, dict) else {}
    language = _showcase_language(showcase)
    collection_title = LANGUAGE_LABELS.get(language or "") if language else None

    chapter_key = meta.chapter_key
    chapter_slug = CHAPTER_ROUTE_SUFFIX.get(chapter_key or "") if chapter_key else None

    return AdminAssignmentPlacement(
        collection_title=collection_title,
        chapter_title=meta.chapter_title,
        chapter_key=chapter_key,
        language=language,
        chapter_slug=chapter_slug,
        teacher_name=teacher_name,
        teacher_email=teacher_email,
    )
