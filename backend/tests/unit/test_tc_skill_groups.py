"""Display TC skill group rollup for student profile."""

from application.curriculum.validation.technical_concept_registry import list_display_tc_cards
from application.learning.display_tc_progress_service import (
    build_display_tc_group_progress,
    build_display_tc_progress,
)
from domain.learning.tc_skill_groups import TC_SKILL_GROUPS, display_tc_group_id


def test_all_display_tc_cards_mapped_to_skill_group():
    mapped = set()
    for group in TC_SKILL_GROUPS:
        mapped.update(group.display_tc_ids)
    for tc_id in list_display_tc_cards():
        assert tc_id in mapped, f"missing group mapping for {tc_id}"


def test_group_progress_dedupes_slot_within_group():
    examples = {
        "curriculum_showcase": {
            "target_language": "pascal",
            "expected_concept_ids": [
                "assignment",
                "variable_declaration",
                "program_root",
            ],
        }
    }

    detail = build_display_tc_progress(
        accessible_task_ids=[1],
        solved_task_ids={1},
        get_code_examples=lambda _tid: examples,
        language="pascal",
        solved_task_ids_by_language={"pascal": {1}},
    )
    groups = build_display_tc_group_progress(
        accessible_task_ids=[1],
        solved_task_ids={1},
        get_code_examples=lambda _tid: examples,
        language="pascal",
        solved_task_ids_by_language={"pascal": {1}},
    )

    basics = next(row for row in groups if row["id"] == "basics")
    assert basics["total"] == 1
    assert basics["solved"] == 1
    assert basics["percent"] == 100.0

    by_id = {row["id"]: row for row in detail}
    assert by_id["tc_assignment"]["total"] == 1
    assert by_id["tc_variables_types"]["total"] == 1
    assert by_id["tc_program_structure"]["total"] == 1


def test_display_tc_group_id_resolves():
    assert display_tc_group_id("tc_loops") == "control_flow"
    assert display_tc_group_id("tc_graphs") == "structures"
