"""Task recommendations from display TC progress."""

from application.learning.tc_task_recommendations_service import (
    build_tc_task_recommendations,
    is_weak_tc_row,
)


def _task(
    task_id: int,
    *,
    title: str = "Задача",
    difficulty: str = "easy",
    concepts: list[str] | None = None,
    slot: str | None = None,
    language: str = "python",
):
    showcase = {
        "expected_concept_ids": concepts or [],
        "target_language": language,
    }
    if slot:
        showcase["slot_id"] = slot
        showcase["pedagogical_slot_id"] = slot

    class Task:
        pass

    row = Task()
    row.title = title
    row.difficulty = difficulty
    row.code_examples = {"curriculum_showcase": showcase}
    row.block_reorder_task = None
    return row


def test_weak_tc_task_is_recommended():
    tc_skills = [
        {"id": "tc_strings", "label": "Строки", "total": 10, "solved": 1, "percent": 10.0},
        {"id": "tc_loops", "label": "Циклы", "total": 10, "solved": 8, "percent": 80.0},
    ]
    tasks = {
        5: _task(
            5,
            title="Подсчёт символов в строке",
            concepts=["string_literal", "counted_loop"],
            slot="rec_strings_01",
        ),
    }

    rows = build_tc_task_recommendations(
        tc_skills=tc_skills,
        accessible_task_ids=[5],
        solved_task_ids=set(),
        get_task=lambda tid: tasks.get(tid),
        get_code_examples=lambda tid: tasks[tid].code_examples if tid in tasks else None,
    )

    assert len(rows) == 1
    assert rows[0]["task_id"] == 5
    assert rows[0]["title"] == "Подсчёт символов в строке"
    assert "tc_strings" in rows[0]["weak_tc_ids"]
    assert rows[0]["score"] == 90.0


def test_task_with_two_weak_tcs_scores_higher():
    tc_skills = [
        {"id": "tc_strings", "label": "Строки", "total": 10, "solved": 2, "percent": 20.0},
        {"id": "tc_functions", "label": "Функции", "total": 8, "solved": 0, "percent": 0.0},
        {"id": "tc_loops", "label": "Циклы", "total": 10, "solved": 8, "percent": 80.0},
    ]
    tasks = {
        1: _task(1, title="Только строки", concepts=["string_literal"], slot="slot_a"),
        2: _task(
            2,
            title="Строки и функции",
            concepts=["string_literal", "function_definition", "counted_loop"],
            slot="slot_b",
        ),
    }

    rows = build_tc_task_recommendations(
        tc_skills=tc_skills,
        accessible_task_ids=[1, 2],
        solved_task_ids=set(),
        get_task=lambda tid: tasks.get(tid),
        get_code_examples=lambda tid: tasks[tid].code_examples if tid in tasks else None,
    )

    assert rows[0]["task_id"] == 2
    assert rows[0]["score"] > rows[1]["score"]


def test_solved_tasks_are_excluded():
    tc_skills = [
        {"id": "tc_strings", "label": "Строки", "total": 5, "solved": 0, "percent": 0.0},
    ]
    tasks = {
        1: _task(1, title="Решена", concepts=["string_literal"], slot="slot_done"),
        2: _task(2, title="Нерешена", concepts=["string_literal"], slot="slot_open"),
    }

    rows = build_tc_task_recommendations(
        tc_skills=tc_skills,
        accessible_task_ids=[1, 2],
        solved_task_ids={1},
        get_task=lambda tid: tasks.get(tid),
        get_code_examples=lambda tid: tasks[tid].code_examples if tid in tasks else None,
    )

    assert [row["task_id"] for row in rows] == [2]


def test_legacy_technical_ids_roll_up_to_display_tc():
    tc_skills = [
        {"id": "tc_strings", "label": "Строки", "total": 5, "solved": 0, "percent": 0.0},
    ]
    tasks = {
        7: _task(7, title="Legacy ids", concepts=["string_literal"], slot="slot_legacy"),
    }

    rows = build_tc_task_recommendations(
        tc_skills=tc_skills,
        accessible_task_ids=[7],
        solved_task_ids=set(),
        get_task=lambda tid: tasks.get(tid),
        get_code_examples=lambda tid: tasks[tid].code_examples if tid in tasks else None,
    )

    assert rows[0]["weak_tc_ids"] == ["tc_strings"]


def test_no_weak_tc_returns_empty_list():
    tc_skills = [
        {"id": "tc_strings", "label": "Строки", "total": 10, "solved": 9, "percent": 90.0},
    ]
    tasks = {1: _task(1, concepts=["string_literal"], slot="slot_a")}

    rows = build_tc_task_recommendations(
        tc_skills=tc_skills,
        accessible_task_ids=[1],
        solved_task_ids=set(),
        get_task=lambda tid: tasks.get(tid),
        get_code_examples=lambda tid: tasks[tid].code_examples if tid in tasks else None,
    )

    assert rows == []


def test_is_weak_tc_requires_min_total():
    assert is_weak_tc_row({"total": 2, "solved": 0, "percent": 0.0}) is False
    assert is_weak_tc_row({"total": 3, "solved": 0, "percent": 39.9}) is True
