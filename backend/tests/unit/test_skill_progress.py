"""Unit tests for concept-based skill groups and progress."""

from application.learning.skill_progress_service import (
    build_skill_progress,
    build_skill_progress_by_language,
)
from domain.learning.skill_groups import (
    CONCEPT_IDS,
    SKILL_GROUPS,
    constructions_to_concepts,
    skill_group_ids_for_constructions,
)


def test_all_concepts_assigned_to_exactly_one_skill_group():
    covered: set[str] = set()
    for group in SKILL_GROUPS:
        covered.update(group.concepts)
    assert covered == set(CONCEPT_IDS)


def test_construction_tags_map_to_concepts():
    assert constructions_to_concepts(["for_loop", "if_statement"]) == {"loop", "condition"}
    assert "loop" in constructions_to_concepts(["loop"])


def test_task_maps_to_skill_groups():
    groups = skill_group_ids_for_constructions(["for_loop", "binary_expression"])
    assert "loops_recursion" in groups
    assert "variables_basics" in groups


def test_skill_progress_percent_from_catalog_tasks():
    tasks = {
        1: ["for_loop"],
        2: ["for_loop"],
        3: ["if_statement"],
    }

    def get_constructions(task_id: int) -> list[str]:
        return tasks.get(task_id, [])

    progress = build_skill_progress(
        accessible_task_ids=[1, 2, 3],
        solved_task_ids={1},
        get_constructions=get_constructions,
    )
    by_id = {row["id"]: row for row in progress}

    assert by_id["loops_recursion"]["total"] == 2
    assert by_id["loops_recursion"]["solved"] == 1
    assert by_id["loops_recursion"]["percent"] == 50.0

    assert by_id["conditions_logic"]["total"] == 1
    assert by_id["conditions_logic"]["solved"] == 0
    assert by_id["conditions_logic"]["percent"] == 0.0

    assert by_id["file_io"]["total"] == 0
    assert by_id["file_io"]["percent"] == 0.0


def test_skill_progress_returns_all_eight_groups():
    progress = build_skill_progress(
        accessible_task_ids=[],
        solved_task_ids=set(),
        get_constructions=lambda _tid: [],
    )
    assert len(progress) == 8
    assert all(row["percent"] == 0.0 for row in progress)


def test_skill_progress_by_language_uses_tracks_and_solved_sets():
    tasks = {
        1: ["for_loop"],
        2: ["if_statement"],
        3: ["for_loop"],
    }

    def get_constructions(task_id: int) -> list[str]:
        return tasks.get(task_id, [])

    def task_languages(task_id: int) -> list[str]:
        if task_id in (1, 2):
            return ["pascal", "python"]
        return ["cpp"]

    by_lang = build_skill_progress_by_language(
        languages=["pascal", "python", "cpp"],
        accessible_task_ids=[1, 2, 3],
        solved_task_ids_by_language={
            "pascal": {1},
            "python": set(),
            "cpp": {3},
        },
        task_languages=task_languages,
        get_constructions=get_constructions,
    )

    pascal_loops = next(
        row for row in by_lang["pascal"] if row["id"] == "loops_recursion"
    )
    assert pascal_loops["total"] == 1
    assert pascal_loops["solved"] == 1

    python_loops = next(
        row for row in by_lang["python"] if row["id"] == "loops_recursion"
    )
    assert python_loops["total"] == 1
    assert python_loops["solved"] == 0

    cpp_loops = next(row for row in by_lang["cpp"] if row["id"] == "loops_recursion")
    assert cpp_loops["total"] == 1
    assert cpp_loops["solved"] == 1
