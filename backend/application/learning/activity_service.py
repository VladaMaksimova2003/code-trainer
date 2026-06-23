"""Суточная активность студента для графика профиля и серии дней."""

from __future__ import annotations

from datetime import timezone

from infrastructure.db.models.learning.submission import Submission

_TERMINAL_STATUSES = frozenset({"done", "failed"})


def submission_counts_as_activity(submission: Submission) -> bool:
    """Засчитывается завершённая проверка решения (успех или провал)."""
    return str(submission.status or "").lower() in _TERMINAL_STATUSES


def build_activity_by_date(submissions: list[Submission]) -> dict[str, int]:
    """
    Ключ даты — ISO UTC (YYYY-MM-DD).
    Значение — число завершённых проверок за день.
    """
    by_date: dict[str, int] = {}
    for submission in submissions:
        if not submission_counts_as_activity(submission):
            continue
        if submission.created_at is None:
            continue
        day = submission.created_at.astimezone(timezone.utc).date().isoformat()
        by_date[day] = by_date.get(day, 0) + 1
    return by_date
