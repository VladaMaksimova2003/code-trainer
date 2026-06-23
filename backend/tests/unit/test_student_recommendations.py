"""Unit tests for student recommendations."""

from application.learning.recommendations.student_recommendations_service import (
    analyze_behavior,
    analyze_errors,
    analyze_progress,
    recommendations_to_legacy_list,
    _started_curriculum_languages,
)
from application.learning.recommendations.student_recommendations_service import (
    StudentInsights,
)


class _FakeSubmission:
    def __init__(self, *, success: bool, error_kind: str = "logic"):
        self.success = success
        self.linter_errors = []
        self.pattern_errors = []
        self.test_results = []
        if error_kind == "syntax":
            self.linter_errors = [type("E", (), {"error_type": "COMPILER"})()]
        elif error_kind == "runtime":
            self.test_results = [
                type(
                    "T",
                    (),
                    {
                        "status": "FAILED",
                        "message": "runtime error: division by zero",
                        "actual": "",
                    },
                )()
            ]


def test_analyze_progress_weak_topic():
    skill_progress = [
        {"label": "Циклы", "percent": 30.0, "total": 5, "solved": 1},
        {"label": "Функции", "percent": 90.0, "total": 4, "solved": 4},
    ]
    weak, steps = analyze_progress(skill_progress)
    assert len(weak) == 1
    assert weak[0]["name"] == "Циклы"
    assert "2–3 задания" in weak[0]["recommendation"]
    assert any("Циклы" in step for step in steps)


def test_analyze_errors_runtime_hint():
    subs = [_FakeSubmission(success=False, error_kind="runtime") for _ in range(4)]
    subs += [_FakeSubmission(success=True)]
    hints = analyze_errors(subs, limit=20)
    assert any("граничных" in hint for hint in hints)


def test_analyze_behavior_streak_message():
    insights = StudentInsights(
        skill_progress=[],
        skill_progress_by_language={},
        submissions=[],
        solved_task_ids=set(),
        solved_task_ids_by_language={},
        accessible_task_ids=set(),
        task_map={},
        activity_by_date={},
        streak_days=5,
    )
    streak, _ = analyze_behavior(insights)
    assert streak["days"] == 5
    assert "5 дней" in streak["message"]


def test_started_curriculum_languages_from_submissions():
    class _Sub:
        def __init__(self, language: str):
            self.language = language

    started = _started_curriculum_languages(
        [_Sub("python"), _Sub("Pascal"), _Sub("javascript")]
    )
    assert started == {"python", "pascal"}


def test_legacy_list_from_structured():
    structured = {
        "streak": {"days": 4, "message": "Серия 4 дня"},
        "weak_topics": [
            {
                "name": "Циклы",
                "progress": 40,
                "recommendation": "Решите 2–3 задачи",
            }
        ],
        "errors": ["Проверьте логику"],
        "next_steps": ["Средний уровень"],
    }
    legacy = recommendations_to_legacy_list(structured)
    assert len(legacy) >= 3
    assert all(item.get("id") != "streak" for item in legacy)
