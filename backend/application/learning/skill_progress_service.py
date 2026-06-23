"""Расчёт прогресса по группам навыков (профиль / аналитика студента)."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable
from typing import Any

from domain.learning.curriculum.constants import SUPPORTED_CURRICULUM_LANGUAGES
from domain.learning.skill_groups import (
    SKILL_GROUPS,
    skill_group_ids_for_constructions,
)

CURRICULUM_LANGUAGE_ORDER: tuple[str, ...] = tuple(
    lang
    for lang in ("pascal", "python", "cpp", "csharp", "java")
    if lang in SUPPORTED_CURRICULUM_LANGUAGES
)

CURRICULUM_LANGUAGE_LABELS: dict[str, str] = {
    "pascal": "Pascal",
    "python": "Python",
    "cpp": "C++",
    "csharp": "C#",
    "java": "Java",
}


def normalize_curriculum_language(language: str | None) -> str | None:
    raw = str(language or "").strip().lower()
    if raw in SUPPORTED_CURRICULUM_LANGUAGES:
        return raw
    if "pascal" in raw:
        return "pascal"
    if "python" in raw or raw == "py":
        return "python"
    if "cpp" in raw or raw == "c++":
        return "cpp"
    return None


def curriculum_languages_for_task(code_examples: dict[str, Any] | None) -> list[str]:
    from application.curriculum.mirror.pedagogical_task_model import available_language_tracks

    showcase = (code_examples or {}).get("curriculum_showcase")
    if isinstance(showcase, dict):
        tracks = available_language_tracks(showcase)
        if tracks:
            return tracks
    return []


def solved_task_ids_by_language(
    submissions: Iterable[Any],
) -> dict[str, set[int]]:
    by_lang: dict[str, set[int]] = defaultdict(set)
    for submission in submissions:
        if getattr(submission, "success", None) is not True:
            continue
        lang = normalize_curriculum_language(getattr(submission, "language", None))
        if not lang:
            continue
        by_lang[lang].add(int(submission.task_id))
    return dict(by_lang)


def build_skill_progress(
    *,
    accessible_task_ids: Iterable[int],
    solved_task_ids: set[int],
    get_constructions: Callable[[int], list[str]],
) -> list[dict[str, Any]]:
    """
    Прогресс группы = (решённые задачи группы / все доступные задачи группы) × 100.

    Задача попадает в группу, если среди её constructions есть хотя бы одна
    концепция из этой группы (см. skill_groups.constructions_to_concepts).
    """
    stats: dict[str, dict[str, int]] = {
        group.id: {"total": 0, "solved": 0} for group in SKILL_GROUPS
    }

    for task_id in accessible_task_ids:
        constructions = get_constructions(task_id)
        group_ids = skill_group_ids_for_constructions(constructions)
        if not group_ids:
            continue
        is_solved = task_id in solved_task_ids
        for group_id in group_ids:
            stats[group_id]["total"] += 1
            if is_solved:
                stats[group_id]["solved"] += 1

    return [
        {
            "id": group.id,
            "label": group.label,
            "hint": group.hint,
            "concepts": list(group.concepts),
            "total": stats[group.id]["total"],
            "solved": stats[group.id]["solved"],
            "percent": round(
                100.0 * stats[group.id]["solved"] / stats[group.id]["total"], 1
            )
            if stats[group.id]["total"]
            else 0.0,
        }
        for group in SKILL_GROUPS
    ]


def build_skill_progress_by_language(
    *,
    languages: Iterable[str] | None = None,
    accessible_task_ids: Iterable[int],
    solved_task_ids_by_language: dict[str, set[int]],
    task_languages: Callable[[int], list[str]],
    get_constructions: Callable[[int], list[str]],
) -> dict[str, list[dict[str, Any]]]:
    """Skill groups scoped to curriculum language tracks and per-language solves."""
    langs = list(languages or CURRICULUM_LANGUAGE_ORDER)
    accessible_set = set(accessible_task_ids)
    result: dict[str, list[dict[str, Any]]] = {}

    for lang in langs:
        lang_key = normalize_curriculum_language(lang) or lang
        if not lang_key:
            continue
        lang_tasks = {
            task_id
            for task_id in accessible_set
            if lang_key in task_languages(task_id)
        }
        solved = solved_task_ids_by_language.get(lang_key, set()) & lang_tasks
        result[lang_key] = build_skill_progress(
            accessible_task_ids=lang_tasks,
            solved_task_ids=solved,
            get_constructions=get_constructions,
        )
    return result
