"""Student-facing C# showcase view."""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from application.curriculum.collections.curriculum_next_service import NEXT_TASK_ACTION_ORDER
from application.curriculum.core.curriculum_service import CurriculumService
from application.curriculum.csharp.showcase.csharp_showcase_next import order_collection_showcase_tasks, _row_from_task
from application.curriculum.csharp.showcase.csharp_v311_registry import v311_collection_by_key
from application.curriculum.csharp.showcase.csharp_v311_showcase_all_specs import all_csharp_v311_showcase_specs
from application.curriculum.display.chapter_task_display_order import student_showcase_task_sort_key
from application.curriculum.display.curriculum_labels import (
    ACTION_LABELS,
    get_action_description_ru,
    get_action_label,
    get_action_skill_label,
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
from application.curriculum.mirror.pedagogical_task_store import learning_language_description
from infrastructure.db.models.task.task import Task as TaskModel

LANGUAGE = "csharp"


def _short_instruction(description: str | None, *, max_len: int = 200) -> str:
    if not description:
        return ""
    text = re.sub(r"```.*?```", "", description.strip(), flags=re.DOTALL)
    text = re.sub(r"\s+", " ", text.replace("\r\n", "\n")).strip()
    first = text.split("\n")[0].strip()
    if len(first) <= max_len:
        return first
    return first[: max_len - 1] + "…"


def _action_sort_key(action: str | None) -> int:
    if not action:
        return len(NEXT_TASK_ACTION_ORDER)
    try:
        return NEXT_TASK_ACTION_ORDER.index(action)
    except ValueError:
        return len(NEXT_TASK_ACTION_ORDER)


def _tc_name_ru(bundle: Any, tc_id: str) -> str:
    tc = bundle.technical_concept_by_id(tc_id)
    return tc.name_ru if tc else tc_id


def _build_task_card(
    *,
    row: dict[str, Any],
    tc_id: str,
    tc_name_ru: str,
    description: str,
    progress_status: str = PROGRESS_STATUS_NOT_STARTED,
    title_prefix: str,
) -> dict[str, Any]:
    action = row.get("action") or ""
    raw_title = str(row.get("title") or "")
    if raw_title.startswith(title_prefix):
        raw_title = raw_title[len(title_prefix):].strip()
    title = strip_showcase_title_prefix(raw_title)
    return {
        "task_id": row["task_id"],
        "slug": row.get("slug"),
        "title": title,
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


def build_csharp_showcase_student_view(
    session: Session,
    chapter_key: str,
    *,
    user_id: int | None = None,
) -> dict[str, Any]:
    col = v311_collection_by_key(chapter_key)
    if col is None:
        raise ValueError(f"Unknown C# chapter: {chapter_key}")

    batch_token = activate_batch_progress_cache(session, user_id)
    try:
        return _build_csharp_showcase_student_body(
            session,
            chapter_key,
            col=col,
            user_id=user_id,
        )
    finally:
        reset_batch_progress_cache(batch_token)


def _build_csharp_showcase_student_body(
    session: Session,
    chapter_key: str,
    *,
    col,
    user_id: int | None,
) -> dict[str, Any]:

    specs = all_csharp_v311_showcase_specs().get(chapter_key, ())
    bundle = CurriculumService(LANGUAGE).get_bundle()
    yaml_chapter = None
    try:
        yaml_chapter = CurriculumService(LANGUAGE).get_learning_concept_detail(LANGUAGE, col.yaml_chapter_id)
    except Exception:
        yaml_chapter = None

    study_order_tc = list(col.study_order_tc)
    showcase_rows = order_collection_showcase_tasks(session, chapter_key, specs)
    task_ids = [int(row["task_id"]) for row in showcase_rows]
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
                tasks_by_tc[tc_id].append(int(row["task_id"]))
        collection_progress = StudentCurriculumProgressService(session).get_progress_for_learning_concept(
            user_id,
            LANGUAGE,
            col.yaml_chapter_id,
            task_ids=task_ids,
            tasks_by_tc=tasks_by_tc,
        )
        for tid, item in collection_progress["by_task_id"].items():
            progress_by_task[int(tid)] = item["progress_status"]

    descriptions: dict[int, str] = {}
    task_rows: dict[int, dict[str, Any]] = {}
    if task_ids:
        for task in session.scalars(select(TaskModel).where(TaskModel.id.in_(task_ids))).all():
            raw_showcase = dict((task.code_examples or {}).get("curriculum_showcase") or {})
            descriptions[task.id] = learning_language_description(raw_showcase, LANGUAGE) or ""
            task_rows[task.id] = _row_from_task(task)

    by_tc: dict[str, list[dict[str, Any]]] = {tc_id: [] for tc_id in study_order_tc}
    for row in showcase_rows:
        task_id = int(row["task_id"])
        enriched = {**row, **task_rows.get(task_id, {})}
        tc_id = resolve_showcase_technical_concept_id(
            enriched.get("technical_concept_id"),
            study_order_tc,
        )
        if not tc_id:
            continue
        by_tc.setdefault(tc_id, []).append(
            enrich_showcase_task_card(
                session,
                user_id,
                _build_task_card(
                    row=enriched,
                    tc_id=tc_id,
                    tc_name_ru=_tc_name_ru(bundle, tc_id),
                    description=descriptions.get(task_id, ""),
                    progress_status=progress_by_task.get(task_id, PROGRESS_STATUS_NOT_STARTED),
                    title_prefix=col.title_prefix,
                ),
            )
        )

    technical_concepts: list[dict[str, Any]] = []
    subtopics: list[dict[str, Any]] = []
    for tc_id in study_order_tc:
        tasks = sorted(
            by_tc.get(tc_id, []),
            key=lambda item: student_showcase_task_sort_key(item, action_sort_key=_action_sort_key),
        )
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
