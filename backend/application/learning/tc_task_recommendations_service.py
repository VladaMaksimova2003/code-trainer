"""Task recommendations from display TC progress — concrete unsolved tasks, not abstract hints."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from application.learning.display_tc_progress_service import (
    _pedagogical_progress_key,
    resolve_display_tc_ids_for_task,
    resolve_display_tc_ids_for_task_for_language,
)
from application.learning.skill_progress_service import (
    curriculum_languages_for_task,
    normalize_curriculum_language,
)
from application.tasks.services.catalog.task_display import display_title_for_task_model

MAX_RECOMMENDATIONS = 3
MAX_REASON_TOPICS = 2
WEAK_MIN_TOTAL = 3
WEAK_MAX_PERCENT = 40.0

_DIFFICULTY_RANK = {
    "easy": 0,
    "легкая": 0,
    "лёгкая": 0,
    "medium": 1,
    "средняя": 1,
    "hard": 2,
    "сложная": 2,
}


def is_weak_tc_row(row: dict[str, Any]) -> bool:
    total = int(row.get("total") or 0)
    percent = float(row.get("percent") or 0)
    return total >= WEAK_MIN_TOTAL and percent < WEAK_MAX_PERCENT


def _difficulty_rank(raw: str | None) -> int:
    key = str(raw or "").strip().lower()
    return _DIFFICULTY_RANK.get(key, 1)


def _reason_for_weak_labels(labels: list[str]) -> str:
    cleaned = [label for label in labels if label]
    if not cleaned:
        return "Мало решённых задач по этой теме"
    head = cleaned[:MAX_REASON_TOPICS]
    if len(cleaned) == 1:
        return f"Подтяните тему «{head[0]}»"
    if len(head) == 1:
        return f"Подтяните тему «{head[0]}»"
    return f"Подтяните темы: {head[0]}, {head[1]}"


def _infer_target_difficulty_rank(
    solved_task_ids: set[int],
    get_task: Callable[[int], Any | None],
) -> int:
    ranks: list[int] = []
    for task_id in solved_task_ids:
        task_model = get_task(int(task_id))
        if task_model is None:
            continue
        ranks.append(_difficulty_rank(getattr(task_model, "difficulty", None)))
    if not ranks:
        return 0
    ranks.sort()
    return ranks[len(ranks) // 2]


def _difficulty_distance(task_rank: int, target_rank: int) -> int:
    if task_rank <= target_rank:
        return target_rank - task_rank
    return task_rank - target_rank + 1


def _task_matches_language(code_examples: dict[str, Any] | None, language: str | None) -> bool:
    lang = normalize_curriculum_language(language)
    if not lang:
        return True
    tracks = curriculum_languages_for_task(code_examples)
    if tracks:
        return lang in tracks
    showcase = (code_examples or {}).get("curriculum_showcase")
    if isinstance(showcase, dict):
        primary = normalize_curriculum_language(
            str(showcase.get("target_language") or showcase.get("language") or "")
        )
        if primary:
            return primary == lang
    return _task_language(code_examples) in {"", lang}


def _sort_weak_tc_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            0 if int(row.get("solved") or 0) == 0 else 1,
            float(row.get("percent") or 0),
            -int(row.get("total") or 0),
        ),
    )


def _slot_solved_map(
    accessible_task_ids: Iterable[int],
    solved_task_ids: set[int],
    get_code_examples: Callable[[int], dict[str, Any] | None],
) -> dict[str, bool]:
    solved_by_slot: dict[str, bool] = {}
    for task_id in accessible_task_ids:
        code_examples = get_code_examples(int(task_id))
        slot_key = _pedagogical_progress_key(int(task_id), code_examples)
        is_solved = int(task_id) in solved_task_ids
        if slot_key in solved_by_slot:
            solved_by_slot[slot_key] = solved_by_slot[slot_key] or is_solved
        else:
            solved_by_slot[slot_key] = is_solved
    return solved_by_slot


def _task_language(code_examples: dict[str, Any] | None) -> str:
    showcase = (code_examples or {}).get("curriculum_showcase")
    if isinstance(showcase, dict):
        lang = showcase.get("target_language") or showcase.get("language")
        if lang:
            return str(lang).strip().lower()
    return ""


def build_tc_task_recommendations(
    *,
    tc_skills: list[dict[str, Any]],
    accessible_task_ids: Iterable[int],
    solved_task_ids: set[int],
    get_task: Callable[[int], Any | None],
    get_code_examples: Callable[[int], dict[str, Any] | None],
    language: str | None = None,
    solved_task_ids_by_language: dict[str, set[int]] | None = None,
) -> list[dict[str, Any]]:
    """
    Pick up to MAX_RECOMMENDATIONS unsolved tasks that best cover weak display TCs
    for the student's level and curriculum language track.
    """
    lang_key = normalize_curriculum_language(language)
    solved_scope = set(solved_task_ids)
    if lang_key and solved_task_ids_by_language:
        solved_scope = set(solved_task_ids_by_language.get(lang_key, set()))

    tc_by_id = {str(row.get("id") or ""): row for row in tc_skills if row.get("id")}
    weak_rows = [row for row in tc_skills if is_weak_tc_row(row)]
    if not weak_rows:
        return []

    weak_tc_ids = {str(row["id"]) for row in weak_rows}
    weak_percent = {str(row["id"]): float(row.get("percent") or 0) for row in weak_rows}
    weak_labels_by_id = {str(row["id"]): str(row.get("label") or row["id"]) for row in weak_rows}
    _sort_weak_tc_rows(weak_rows)
    target_difficulty = _infer_target_difficulty_rank(solved_scope, get_task)

    slot_solved = _slot_solved_map(accessible_task_ids, solved_scope, get_code_examples)

    candidates: list[dict[str, Any]] = []
    seen_slots: set[str] = set()
    for task_id in sorted(int(tid) for tid in accessible_task_ids):
        if task_id in solved_scope:
            continue

        code_examples = get_code_examples(task_id)
        if not _task_matches_language(code_examples, lang_key):
            continue

        slot_key = _pedagogical_progress_key(task_id, code_examples)
        if slot_key in seen_slots:
            continue
        seen_slots.add(slot_key)
        if slot_solved.get(slot_key):
            continue

        if lang_key:
            display_ids = resolve_display_tc_ids_for_task_for_language(code_examples, lang_key)
        else:
            display_ids = resolve_display_tc_ids_for_task(code_examples)
        weak_on_task = display_ids & weak_tc_ids
        if not weak_on_task:
            continue

        task_model = get_task(task_id)
        title = (
            display_title_for_task_model(task_model)
            if task_model is not None
            else f"Задача #{task_id}"
        )
        difficulty = str(getattr(task_model, "difficulty", None) or "medium")
        language_value = lang_key or _task_language(code_examples)
        if not language_value and task_model is not None:
            block = getattr(task_model, "block_reorder_task", None)
            if block is not None:
                language_value = str(getattr(block, "language", "") or "").strip().lower()

        score = sum(100.0 - weak_percent[tc_id] for tc_id in weak_on_task)
        diff_rank = _difficulty_rank(difficulty)
        diff_distance = _difficulty_distance(diff_rank, target_difficulty)
        resolved_count = sum(
            1 for tc_id in display_ids if tc_id in tc_by_id and not is_weak_tc_row(tc_by_id[tc_id])
        )
        weak_sorted = sorted(
            weak_on_task,
            key=lambda tc_id: (
                0 if int(tc_by_id.get(tc_id, {}).get("solved") or 0) == 0 else 1,
                float(tc_by_id.get(tc_id, {}).get("percent") or 0),
                -int(tc_by_id.get(tc_id, {}).get("total") or 0),
            ),
        )
        weak_labels = [weak_labels_by_id[tc_id] for tc_id in weak_sorted]

        candidates.append(
            {
                "task_id": task_id,
                "title": title,
                "language": language_value or "python",
                "difficulty": difficulty,
                "reason": _reason_for_weak_labels(weak_labels),
                "weak_tc_ids": list(weak_sorted[:MAX_REASON_TOPICS]),
                "weak_tc_labels": weak_labels[:MAX_REASON_TOPICS],
                "score": round(score, 1),
                "_sort": (
                    diff_distance,
                    -score,
                    diff_rank,
                    -resolved_count,
                    task_id,
                ),
            }
        )

    candidates.sort(key=lambda item: item["_sort"])
    results: list[dict[str, Any]] = []
    for item in candidates[:MAX_RECOMMENDATIONS]:
        payload = {key: value for key, value in item.items() if not key.startswith("_")}
        results.append(payload)
    return results
