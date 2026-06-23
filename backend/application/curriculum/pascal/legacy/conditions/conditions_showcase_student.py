"""Student-facing view — Pascal / LC conditions showcase grouped by TC."""

from __future__ import annotations

import re
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from application.curriculum.pascal.legacy.conditions.conditions_showcase_seeder import list_showcase_tasks
from application.curriculum.display.curriculum_labels import (
    ACTION_LABELS,
    get_action_description_ru,
    get_action_label,
    get_action_skill_label,
)
from application.curriculum.core.curriculum_service import CurriculumService
from application.curriculum.display.showcase_display import strip_showcase_title_prefix
from application.curriculum.progress.student_curriculum_progress_service import (
    PROGRESS_STATUS_NOT_STARTED,
    StudentCurriculumProgressService,
)
from infrastructure.db.models.task.task import Task as TaskModel

LANGUAGE = "pascal"
LEARNING_CONCEPT_ID = "conditions"

ACTION_ORDER = ("translate", "assemble", "implement", "analyze", "debug", "recognize")


def _display_title(title: str) -> str:
    return strip_showcase_title_prefix(title or "")


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
        return len(ACTION_ORDER)
    try:
        return ACTION_ORDER.index(action)
    except ValueError:
        return len(ACTION_ORDER)


def _build_task_card(
    *,
    row: dict[str, Any],
    tc_id: str,
    tc_name_ru: str,
    learning_concept: dict[str, Any],
    description: str,
    progress_status: str = PROGRESS_STATUS_NOT_STARTED,
) -> dict[str, Any]:
    action = row.get("action") or ""
    return {
        "task_id": row["task_id"],
        "slug": row.get("slug"),
        "title": _display_title(row.get("title") or ""),
        "task_type": row.get("task_type"),
        "difficulty": row.get("difficulty"),
        "technical_concept_name_ru": tc_name_ru,
        "action": action,
        "action_label": get_action_label(action),
        "action_skill_label": get_action_skill_label(action),
        "action_description_ru": get_action_description_ru(action),
        "short_instruction": _short_instruction(description),
        "progress_status": progress_status,
    }


def build_pascal_conditions_showcase_student_view(
    session: Session,
    *,
    user_id: int | None = None,
) -> dict[str, Any]:
    curriculum = CurriculumService(LANGUAGE)
    chapter = curriculum.get_learning_concept_detail(LANGUAGE, LEARNING_CONCEPT_ID)
    learning_concept = chapter["learning_concept"]
    study_order_tc = list(chapter["study_order_tc"])
    tc_meta = {tc["id"]: tc for tc in chapter["technical_concepts"]}

    showcase_rows = list_showcase_tasks(session)
    task_ids = [row["task_id"] for row in showcase_rows]
    progress_by_task: dict[int, str] = {}
    lc_progress: dict[str, Any] | None = None
    if user_id is not None and task_ids:
        tasks_by_tc: dict[str, list[int]] = {tc_id: [] for tc_id in study_order_tc}
        for row in showcase_rows:
            tc_id = row.get("technical_concept_id")
            if tc_id in tasks_by_tc:
                tasks_by_tc[tc_id].append(row["task_id"])
        lc_progress = StudentCurriculumProgressService(session).get_progress_for_learning_concept(
            user_id,
            LANGUAGE,
            LEARNING_CONCEPT_ID,
            task_ids=task_ids,
            tasks_by_tc=tasks_by_tc,
        )
        for tid, item in lc_progress["by_task_id"].items():
            progress_by_task[int(tid)] = item["progress_status"]
    descriptions: dict[int, str] = {}
    if task_ids:
        for task in session.scalars(select(TaskModel).where(TaskModel.id.in_(task_ids))).all():
            descriptions[task.id] = task.description or ""

    by_tc: dict[str, list[dict[str, Any]]] = {tc_id: [] for tc_id in study_order_tc}
    for row in showcase_rows:
        tc_id = row.get("technical_concept_id")
        if not tc_id or tc_id not in by_tc:
            continue
        meta = tc_meta.get(tc_id, {})
        by_tc[tc_id].append(
            _build_task_card(
                row=row,
                tc_id=tc_id,
                tc_name_ru=meta.get("name_ru", tc_id),
                learning_concept=learning_concept,
                description=descriptions.get(row["task_id"], ""),
                progress_status=progress_by_task.get(row["task_id"], PROGRESS_STATUS_NOT_STARTED),
            )
        )

    technical_concepts: list[dict[str, Any]] = []
    for tc_id in study_order_tc:
        meta = tc_meta.get(tc_id, {})
        tasks = sorted(by_tc.get(tc_id, []), key=lambda item: _action_sort_key(item.get("action")))
        tc_progress = None
        if lc_progress and tc_id in lc_progress.get("by_technical_concept", {}):
            tc_progress = lc_progress["by_technical_concept"][tc_id]
        technical_concepts.append(
            {
                "id": tc_id,
                "name_ru": meta.get("name_ru", tc_id),
                "tier": meta.get("tier"),
                "tasks": tasks,
                "progress": tc_progress,
            }
        )

    total_tasks = sum(len(tc["tasks"]) for tc in technical_concepts)

    result: dict[str, Any] = {
        "language": LANGUAGE,
        "learning_concept": learning_concept,
        "study_order_tc": study_order_tc,
        "technical_concepts": technical_concepts,
        "total_tasks": total_tasks,
        "labels": {
            "actions": {
                action: {
                    "badge": ACTION_LABELS[action],
                    "skill": get_action_skill_label(action),
                    "description_ru": get_action_description_ru(action),
                }
                for action in ACTION_LABELS
            },
        },
    }
    if lc_progress is not None:
        result["progress"] = {
            "total_tasks": lc_progress["total_tasks"],
            "passed_tasks": lc_progress["passed_tasks"],
            "progress_percent": lc_progress["progress_percent"],
        }
    return result

