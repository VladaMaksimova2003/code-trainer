"""
Генерация персональных рекомендаций студента на основе аналитики, попыток и поведения.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session, joinedload

from application.auth.dto import CurrentUserResult
from application.learning.activity_service import build_activity_by_date
from application.learning.skill_progress_service import (
    CURRICULUM_LANGUAGE_LABELS,
    CURRICULUM_LANGUAGE_ORDER,
    build_skill_progress,
    build_skill_progress_by_language,
    curriculum_languages_for_task,
    normalize_curriculum_language,
    solved_task_ids_by_language,
)
from application.learning.submission_analytics import (
    classify_submission_errors,
    load_task_map,
    task_constructions,
)
from application.tasks.services.content_access_service import ContentAccessService
from domain.policies.rbac.rbac import normalize_role, primary_role
from infrastructure.db.models.learning.submission import Submission
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.models.user.user import User
from infrastructure.db.models.user.user_role import UserRole
from shared.enums import UserType

RECENT_SUBMISSIONS_LIMIT = 20
ERROR_SHARE_THRESHOLD = 0.35
MIN_ERRORS_FOR_HINT = 2

_PROGRESS_WEAK_MAX = 50.0
_PROGRESS_SOLID_MAX = 80.0


@dataclass(frozen=True)
class StudentInsights:
    skill_progress: list[dict[str, Any]]
    skill_progress_by_language: dict[str, list[dict[str, Any]]]
    submissions: list[Submission]
    solved_task_ids: set[int]
    solved_task_ids_by_language: dict[str, set[int]]
    accessible_task_ids: set[int]
    task_map: dict[int, TaskModel]
    activity_by_date: dict[str, int]
    streak_days: int


def _viewer_for_user_id(db: Session, user_id: int) -> CurrentUserResult:
    user = db.get(User, user_id)
    if user is None:
        raise ValueError(f"User {user_id} not found")
    role_rows = db.query(UserRole).filter(UserRole.user_id == user_id).all()
    roles = [normalize_role(row.role) for row in role_rows]
    if not roles:
        roles = [UserType.STUDENT]
    role_set = frozenset(roles)
    return CurrentUserResult(
        id=user.id,
        name=user.name or "",
        email=user.email or "",
        role=primary_role(role_set),
        roles=sorted(role_set, key=lambda r: r.value),
    )


def _streak_from_activity(by_date: dict[str, int]) -> int:
    today = datetime.now(timezone.utc).date()
    cursor = today
    if not by_date.get(today.isoformat()):
        cursor = today - timedelta(days=1)
    streak = 0
    while by_date.get(cursor.isoformat(), 0) > 0:
        streak += 1
        cursor = cursor - timedelta(days=1)
    return streak


def gather_student_insights(db: Session, viewer: CurrentUserResult) -> StudentInsights:
    uid = viewer.id
    roles = frozenset(normalize_role(r) for r in viewer.roles)
    access = ContentAccessService(db)
    accessible_ids = set(access.list_accessible_task_ids(uid, roles))

    submissions = (
        db.query(Submission)
        .options(
            joinedload(Submission.linter_errors),
            joinedload(Submission.pattern_errors),
            joinedload(Submission.test_results),
        )
        .filter(Submission.user_id == uid)
        .order_by(Submission.created_at.desc())
        .all()
    )

    task_attempts: dict[int, list[Submission]] = defaultdict(list)
    for submission in submissions:
        task_attempts[submission.task_id].append(submission)

    solved_task_ids = {
        task_id
        for task_id, attempts in task_attempts.items()
        if any(item.success is True for item in attempts)
    }

    accessible_task_map = load_task_map(db, accessible_ids)

    def constructions_for_task(task_id: int) -> list[str]:
        task = accessible_task_map.get(task_id)
        if task is None:
            return []
        return task_constructions(db, task)

    skill_progress = build_skill_progress(
        accessible_task_ids=accessible_ids,
        solved_task_ids=solved_task_ids,
        get_constructions=constructions_for_task,
    )

    solved_by_language = solved_task_ids_by_language(submissions)

    def task_languages(task_id: int) -> list[str]:
        task = accessible_task_map.get(task_id)
        if task is None:
            return []
        tracks = curriculum_languages_for_task(task.code_examples)
        if tracks:
            return tracks
        block = getattr(task, "block_reorder_task", None)
        if block is not None:
            lang = normalize_curriculum_language(getattr(block, "language", None))
            return [lang] if lang else []
        translation = getattr(task, "translation_task", None)
        if translation is not None:
            langs: list[str] = []
            for candidate in (
                getattr(translation, "source_language", None),
                getattr(translation, "target_language", None),
            ):
                norm = normalize_curriculum_language(candidate)
                if norm and norm not in langs:
                    langs.append(norm)
            if langs:
                return langs
        return []

    skill_progress_by_language = build_skill_progress_by_language(
        languages=CURRICULUM_LANGUAGE_ORDER,
        accessible_task_ids=accessible_ids,
        solved_task_ids_by_language=solved_by_language,
        task_languages=task_languages,
        get_constructions=constructions_for_task,
    )

    activity_by_date = build_activity_by_date(submissions)
    streak_days = _streak_from_activity(activity_by_date)

    attempted_task_ids = set(task_attempts.keys())
    task_map = load_task_map(db, attempted_task_ids | accessible_ids)

    return StudentInsights(
        skill_progress=skill_progress,
        skill_progress_by_language=skill_progress_by_language,
        submissions=submissions,
        solved_task_ids=solved_task_ids,
        solved_task_ids_by_language=solved_by_language,
        accessible_task_ids=accessible_ids,
        task_map=task_map,
        activity_by_date=activity_by_date,
        streak_days=streak_days,
    )


def _progress_recommendation(label: str, percent: float) -> str:
    if percent < _PROGRESS_WEAK_MAX:
        return f"Рекомендуется решить 2–3 задания по теме «{label}»"
    if percent <= _PROGRESS_SOLID_MAX:
        return f"Рекомендуется закрепить тему «{label}»"
    return f"Можно переходить к более сложным задачам по теме «{label}»"


def analyze_progress(skill_progress: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    """Слабые темы и шаги по прогрессу навыков."""
    weak_topics: list[dict[str, Any]] = []
    next_steps: list[str] = []

    ranked = sorted(
        [row for row in skill_progress if row.get("total", 0) > 0],
        key=lambda row: (row.get("percent", 0), -row.get("total", 0)),
    )

    for row in ranked:
        percent = float(row.get("percent", 0))
        label = str(row.get("label", ""))
        if percent < _PROGRESS_WEAK_MAX:
            weak_topics.append(
                {
                    "name": label,
                    "progress": round(percent, 1),
                    "recommendation": _progress_recommendation(label, percent),
                }
            )

    if ranked:
        weakest = ranked[0]
        weakest_label = str(weakest.get("label", ""))
        weakest_percent = float(weakest.get("percent", 0))
        next_steps.append(f"Рекомендуется перейти к теме: {weakest_label}")

        for row in ranked[1:3]:
            percent = float(row.get("percent", 0))
            label = str(row.get("label", ""))
            if _PROGRESS_WEAK_MAX <= percent <= _PROGRESS_SOLID_MAX:
                next_steps.append(_progress_recommendation(label, percent))

        strong = [row for row in ranked if float(row.get("percent", 0)) > _PROGRESS_SOLID_MAX]
        if strong:
            best = max(strong, key=lambda row: float(row.get("percent", 0)))
            next_steps.append(
                _progress_recommendation(str(best.get("label", "")), float(best.get("percent", 0)))
            )
        elif weakest_percent > _PROGRESS_SOLID_MAX:
            next_steps.append(_progress_recommendation(weakest_label, weakest_percent))

    return weak_topics, next_steps


def analyze_errors(submissions: list[Submission], *, limit: int = RECENT_SUBMISSIONS_LIMIT) -> list[str]:
    """Подсказки по типам ошибок в последних попытках."""
    recent = submissions[:limit]
    failed = [item for item in recent if item.success is False]
    if not failed:
        return []

    counts = {"syntax": 0, "logic": 0, "runtime": 0}
    for submission in failed:
        category = classify_submission_errors(submission)
        if category in counts:
            counts[category] += 1

    total_failed = len(failed)
    hints: list[str] = []

    if counts["runtime"] >= max(MIN_ERRORS_FOR_HINT, total_failed * ERROR_SHARE_THRESHOLD):
        hints.append(
            "Частые ошибки выполнения — обратите внимание на обработку граничных условий"
        )
    if counts["logic"] >= max(MIN_ERRORS_FOR_HINT, total_failed * ERROR_SHARE_THRESHOLD):
        hints.append("Рекомендуется внимательнее проверять логику решения")
    if counts["syntax"] >= max(MIN_ERRORS_FOR_HINT, total_failed * ERROR_SHARE_THRESHOLD):
        hints.append("Обратите внимание на синтаксис выбранного языка")

    return hints


def _normalize_difficulty(raw: str | None) -> str:
    return str(raw or "").strip().lower()


def analyze_behavior(
    insights: StudentInsights,
) -> tuple[dict[str, Any], list[str]]:
    """Серия дней и рекомендации по сложности задач."""
    streak_days = insights.streak_days
    if streak_days >= 3:
        streak_message = (
            f"Вы занимаетесь {streak_days} дней подряд — отличная регулярность"
        )
    elif streak_days > 0:
        streak_message = (
            f"Продолжайте заниматься, чтобы сохранить серию ({streak_days} дн.)"
        )
    else:
        streak_message = "Решите любую задачу сегодня — так начнётся серия дней"

    streak = {"days": streak_days, "message": streak_message}
    next_steps: list[str] = []

    difficulty_stats: dict[str, int] = defaultdict(int)
    for task_id in insights.solved_task_ids | set(
        s.task_id for s in insights.submissions
    ):
        task = insights.task_map.get(task_id)
        if task is None:
            continue
        difficulty_stats[_normalize_difficulty(task.difficulty)] += 1

    easy_count = difficulty_stats.get("easy", 0)
    medium_count = difficulty_stats.get("medium", 0)
    hard_count = difficulty_stats.get("hard", 0)
    total_labeled = easy_count + medium_count + hard_count
    if total_labeled >= 3 and medium_count == 0 and hard_count == 0:
        next_steps.append("Попробуйте задания среднего уровня")

    return streak, next_steps


def _submissions_for_language(
    submissions: list[Submission],
    language: str,
) -> list[Submission]:
    lang = normalize_curriculum_language(language) or language
    return [
        item
        for item in submissions
        if normalize_curriculum_language(item.language) == lang
    ]


def _started_curriculum_languages(submissions: list[Submission]) -> set[str]:
    started: set[str] = set()
    for submission in submissions:
        lang = normalize_curriculum_language(submission.language)
        if lang:
            started.add(lang)
    return started


def _recommendations_for_language(
    *,
    language: str,
    skills: list[dict[str, Any]],
    submissions: list[Submission],
) -> dict[str, Any]:
    weak_topics, next_steps = analyze_progress(skills)
    errors = analyze_errors(_submissions_for_language(submissions, language))
    visible_skills = [row for row in skills if int(row.get("total") or 0) > 0]
    return {
        "language": language,
        "language_label": CURRICULUM_LANGUAGE_LABELS.get(language, language),
        "skills": visible_skills,
        "weak_topics": weak_topics,
        "errors": errors,
        "next_steps": next_steps,
    }


def get_student_recommendations(db: Session, user_id: int) -> dict[str, Any]:
    viewer = _viewer_for_user_id(db, user_id)
    insights = gather_student_insights(db, viewer)

    weak_topics, progress_steps = analyze_progress(insights.skill_progress)
    error_hints = analyze_errors(insights.submissions)
    streak, behavior_steps = analyze_behavior(insights)

    by_language: dict[str, dict[str, Any]] = {}
    started_langs = _started_curriculum_languages(insights.submissions)
    for lang in CURRICULUM_LANGUAGE_ORDER:
        if lang not in started_langs:
            continue
        skills = insights.skill_progress_by_language.get(lang, [])
        if not any(row.get("total", 0) > 0 for row in skills):
            continue
        by_language[lang] = _recommendations_for_language(
            language=lang,
            skills=skills,
            submissions=insights.submissions,
        )

    next_steps: list[str] = []
    seen: set[str] = set()
    for step in progress_steps + behavior_steps:
        if step not in seen:
            seen.add(step)
            next_steps.append(step)

    if not weak_topics and not error_hints and not next_steps and insights.solved_task_ids:
        next_steps.append("Продолжайте решать задачи из каталога — прогресс равномерный")

    return {
        "streak": streak,
        "weak_topics": weak_topics,
        "errors": error_hints,
        "next_steps": next_steps,
        "by_language": by_language,
    }


def recommendations_to_legacy_list(structured: dict[str, Any]) -> list[dict[str, str]]:
    """Формат для существующего UI (список с kind / message)."""
    items: list[dict[str, str]] = []

    for index, topic in enumerate(structured.get("weak_topics") or []):
        items.append(
            {
                "kind": "hint",
                "message": topic.get("recommendation") or topic.get("name", ""),
                "detail": topic.get("name", ""),
                "id": f"weak-{index}",
            }
        )

    for index, error_text in enumerate(structured.get("errors") or []):
        items.append({"kind": "hint", "message": error_text, "id": f"error-{index}"})

    for index, step in enumerate(structured.get("next_steps") or []):
        items.append({"kind": "hint", "message": step, "id": f"step-{index}"})

    return items
