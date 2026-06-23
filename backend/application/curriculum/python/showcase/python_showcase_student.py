"""Student-facing Python showcase view (any collection)."""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from application.curriculum.display.chapter_task_display_order import student_showcase_task_sort_key
from application.curriculum.display.curriculum_labels import (
    ACTION_LABELS,
    get_action_description_ru,
    get_action_label,
    get_action_skill_label,
)
from application.curriculum.core.curriculum_service import CurriculumService
from application.curriculum.python.showcase.python_showcase_core import (
    list_showcase_tasks_for_collection,
)

_V311_CURRICULUM_VERSION = "1.0"


def _resolve_collection(chapter_key: str):
    v311 = v311_collection_by_key(chapter_key)
    if v311 is not None:
        return v311
    return collection_by_key(chapter_key)


def _is_v311_col(col) -> bool:
    return isinstance(col, PythonV311Collection)
from application.curriculum.pascal.showcase.pascal_showcase_registry import (
    PascalShowcaseCollection,
    collection_by_key,
)
from application.curriculum.python.showcase.python_v311_registry import (
    v311_collection_by_key,
    PythonV311Collection,
)
from application.curriculum.display.showcase_display import (
    resolve_showcase_technical_concept_id,
    strip_showcase_title_prefix,
)
from application.curriculum.progress.student_curriculum_progress_service import (
    PROGRESS_STATUS_NOT_STARTED,
    StudentCurriculumProgressService,
    activate_batch_progress_cache,
    reset_batch_progress_cache,
)
from application.curriculum.showcase.showcase_language_progress import enrich_showcase_task_card
from infrastructure.db.models.task.task import Task as TaskModel

LANGUAGE = "python"


def _short_instruction(description: str | None, *, max_len: int = 200) -> str:
    if not description:
        return ""
    text = re.sub(r"```.*?```", "", description.strip(), flags=re.DOTALL)
    text = re.sub(r"\s+", " ", text.replace("\r\n", "\n")).strip()
    first = text.split("\n")[0].strip()
    if len(first) <= max_len:
        return first
    return first[: max_len - 1] + "…"


def _tc_name_ru(bundle, tc_id: str) -> str:
    tc = bundle.technical_concept_by_id(tc_id)
    return tc.name_ru if tc else tc_id


def _build_task_card(
    *,
    row: dict[str, Any],
    tc_id: str,
    tc_name_ru: str,
    description: str,
    progress_status: str = PROGRESS_STATUS_NOT_STARTED,
) -> dict[str, Any]:
    action = row.get("action") or ""
    return {
        "task_id": row["task_id"],
        "slug": row.get("slug"),
        "title": strip_showcase_title_prefix(str(row.get("title") or "")),
        "task_type": row.get("task_type"),
        "difficulty": row.get("difficulty"),
        "technical_concept_name_ru": tc_name_ru,
        "subtopic_name_ru": tc_name_ru,
        "action": action,
        "action_label": get_action_label(action),
        "action_skill_label": get_action_skill_label(action, language=LANGUAGE),
        "action_description_ru": get_action_description_ru(action, language=LANGUAGE),
        "short_instruction": _short_instruction(description),
        "display_order": row.get("display_order"),
        "progress_status": progress_status,
    }


def build_python_showcase_student_view(
    session: Session,
    chapter_key: str,
    *,
    user_id: int | None = None,
) -> dict[str, Any]:
    col = _resolve_collection(chapter_key)
    if col is None:
        from application.curriculum.chapters.curriculum_chapter_meta_service import (
            custom_showcase_collection,
            list_custom_chapters_for_language,
        )

        if any(item.chapter_key == chapter_key for item in list_custom_chapters_for_language(session, LANGUAGE)):
            col = custom_showcase_collection(session, LANGUAGE, chapter_key)
        else:
            raise ValueError(f"Unknown showcase collection: {chapter_key}")

    return _build_python_showcase_student_view_impl(
        session,
        chapter_key,
        col=col,
        user_id=user_id,
    )


def _build_python_showcase_student_view_impl(
    session: Session,
    chapter_key: str,
    *,
    col,
    user_id: int | None = None,
) -> dict[str, Any]:
    is_v311 = _is_v311_col(col)
    curriculum_version = _V311_CURRICULUM_VERSION if is_v311 else None

    batch_token = activate_batch_progress_cache(session, user_id)
    try:
        return _build_python_showcase_student_view_body(
            session,
            chapter_key,
            col=col,
            user_id=user_id,
            is_v311=is_v311,
        )
    finally:
        reset_batch_progress_cache(batch_token)


def _build_python_showcase_student_view_body(
    session: Session,
    chapter_key: str,
    *,
    col,
    user_id: int | None,
    is_v311: bool,
) -> dict[str, Any]:
    curriculum_version = _V311_CURRICULUM_VERSION if is_v311 else None

    bundle = CurriculumService(LANGUAGE).get_bundle()
    yaml_chapter = None
    try:
        yaml_chapter = CurriculumService(LANGUAGE).get_learning_concept_detail(
            LANGUAGE, col.yaml_chapter_id
        )
    except Exception:
        yaml_chapter = None

    study_order_tc = list(col.study_order_tc)
    showcase_rows = list_showcase_tasks_for_collection(
        session, chapter_key, curriculum_version=_V311_CURRICULUM_VERSION if is_v311 else "2"
    )
    if not study_order_tc and showcase_rows:
        study_order_tc = ["general"]
    task_ids = [row["task_id"] for row in showcase_rows]
    progress_by_task: dict[int, str] = {}
    collection_progress: dict[str, Any] | None = None

    if user_id is not None and task_ids:
        tasks_by_tc: dict[str, list[int]] = {tc_id: [] for tc_id in study_order_tc}
        for row in showcase_rows:
            tc_id = resolve_showcase_technical_concept_id(
                row.get("technical_concept_id"),
                study_order_tc,
            )
            if tc_id in tasks_by_tc:
                tasks_by_tc[tc_id].append(row["task_id"])
        collection_progress = StudentCurriculumProgressService(session).get_progress_for_learning_concept(
            user_id,
            LANGUAGE,
            col.yaml_chapter_id,
            task_ids=task_ids,
            tasks_by_tc=tasks_by_tc,
        )
        for tid, item in collection_progress["by_task_id"].items():
            progress_by_task[int(tid)] = item["progress_status"]

    from application.curriculum.python.catalog.python_catalog_runtime import (
        educational_goal_for_slot,
        is_v4_python_slot,
    )

    descriptions: dict[int, str] = {}
    if task_ids and not is_v311:
        from sqlalchemy.orm import load_only

        stmt = (
            select(TaskModel)
            .options(load_only(TaskModel.id, TaskModel.description))
            .where(TaskModel.id.in_(task_ids))
        )
        for task in session.scalars(stmt).all():
            descriptions[task.id] = task.description or ""

    def _description_for_row(row: dict[str, Any]) -> str:
        slug = str(row.get("slug") or "").strip()
        if is_v311 and slug and is_v4_python_slot(slug):
            goal = educational_goal_for_slot(slug)
            if goal:
                return goal
        return descriptions.get(int(row["task_id"]), "")

    by_tc: dict[str, list[dict[str, Any]]] = {tc_id: [] for tc_id in study_order_tc}
    for row in showcase_rows:
        tc_id = resolve_showcase_technical_concept_id(
            row.get("technical_concept_id"),
            study_order_tc,
        )
        if not tc_id:
            continue
        card = _build_task_card(
            row=row,
            tc_id=tc_id,
            tc_name_ru=_tc_name_ru(bundle, tc_id),
            description=_description_for_row(row),
            progress_status=progress_by_task.get(row["task_id"], PROGRESS_STATUS_NOT_STARTED),
        )
        if user_id is not None:
            card = enrich_showcase_task_card(session, user_id, card)
        by_tc.setdefault(tc_id, []).append(card)

    technical_concepts: list[dict[str, Any]] = []
    subtopics: list[dict[str, Any]] = []
    for tc_id in study_order_tc:
        tasks = sorted(by_tc.get(tc_id, []), key=student_showcase_task_sort_key)
        tc_progress = None
        if collection_progress and tc_id in collection_progress.get("by_technical_concept", {}):
            tc_progress = collection_progress["by_technical_concept"][tc_id]
        section = {
            "name_ru": _tc_name_ru(bundle, tc_id),
            "tasks": tasks,
            "progress": tc_progress,
        }
        technical_concepts.append({"id": tc_id, **section})
        subtopics.append(section)

    lc = yaml_chapter["learning_concept"] if yaml_chapter else {
        "id": col.yaml_chapter_id,
        "name_ru": col.title_ru,
        "description_ru": col.description_ru,
    }

    result: dict[str, Any] = {
        "language": LANGUAGE,
        "collection_key": chapter_key,
        "collection_id": col.collection_id,
        "title_ru": col.title_ru,
        "description_ru": col.description_ru,
        "learning_concept": lc,
        "theme": lc,
        "subtopics": subtopics,
        "technical_concepts": technical_concepts,
        "total_tasks": sum(len(section["tasks"]) for section in subtopics),
        "labels": {
            "actions": {
                action: {
                    "badge": ACTION_LABELS[action],
                    "skill": get_action_skill_label(action, language=LANGUAGE),
                    "description_ru": get_action_description_ru(action, language=LANGUAGE),
                }
                for action in ACTION_LABELS
            },
        },
    }
    if collection_progress is not None:
        result["progress"] = {
            "total_tasks": collection_progress["total_tasks"],
            "passed_tasks": collection_progress["passed_tasks"],
            "progress_percent": collection_progress["progress_percent"],
        }
    return result

