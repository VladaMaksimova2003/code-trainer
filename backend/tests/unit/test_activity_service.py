from datetime import datetime, timezone

from application.learning.activity_service import build_activity_by_date


class _Sub:
    def __init__(self, *, status: str, created_at: datetime | None):
        self.status = status
        self.created_at = created_at


def test_build_activity_counts_terminal_submissions_only():
    day = datetime(2026, 6, 11, 12, 0, tzinfo=timezone.utc)
    subs = [
        _Sub(status="done", created_at=day),
        _Sub(status="failed", created_at=day),
        _Sub(status="queued", created_at=day),
        _Sub(status="running", created_at=day),
    ]
    assert build_activity_by_date(subs) == {"2026-06-11": 2}
