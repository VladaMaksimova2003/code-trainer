"""Unit tests — curriculum v2, loops chapter viability."""

from __future__ import annotations

import pytest

from application.curriculum.core.curriculum_service import CurriculumService
from domain.learning.curriculum.exceptions import CurriculumValidationError
from infrastructure.curriculum.loader import load_curriculum, validate_curriculum_bundle

LOOPS_TC = (
    "counted_loop",
    "pre_condition_loop",
    "post_condition_loop",
    "collection_iteration",
    "nested_iteration",
    "loop_control",
)


@pytest.fixture(scope="module")
def bundle():
    return load_curriculum("pascal", force=True)


@pytest.fixture(scope="module")
def service():
    return CurriculumService("pascal")


def test_curriculum_loads_and_validates(bundle):
    errors = validate_curriculum_bundle(bundle)
    assert errors == []


def test_validate_curriculum_service(service):
    result = service.validate_curriculum("pascal")
    assert result["valid"] is True
    assert result["errors"] == []
    assert result["stats"]["technical_concepts"] >= 60
    assert result["stats"]["exercise_patterns"] == 26


def test_counted_loop_has_six_active_actions(bundle):
    mask = bundle.action_masks["counted_loop"]
    assert set(mask.active_actions()) == {
        "recognize",
        "assemble",
        "translate",
        "analyze",
        "debug",
        "implement",
    }
    assert mask.disabled_actions == ()


def test_loop_control_has_disabled_assemble(bundle):
    mask = bundle.action_masks["loop_control"]
    assert "assemble" in mask.disabled_actions
    assert "assemble" not in mask.required_actions
    assert "assemble" not in mask.active_actions()
    assert len(mask.active_actions()) == 5


def test_collection_iteration_no_required_flowchart_assemble(bundle):
    mask = bundle.action_masks["collection_iteration"]
    required_assemble = mask.patterns_for_action("assemble", required_only=True)
    assert required_assemble == ("asm_blocks_to_code_pascal",)
    assert "asm_flowchart_to_blocks" not in required_assemble
    disabled_asm = mask.disabled_patterns_by_action.get("assemble", ())
    assert "asm_flowchart_to_blocks" in disabled_asm


def test_loops_required_patterns_exist_in_catalog(bundle):
    catalog_ids = {p.id for p in bundle.exercise_patterns}
    for tc_id in LOOPS_TC:
        mask = bundle.action_masks[tc_id]
        for action in mask.active_actions():
            for pid in mask.patterns_for_action(action, required_only=True):
                assert pid in catalog_ids, f"{tc_id}/{action}: missing {pid}"


def test_loops_mandatory_pattern_slots_count_is_54(bundle):
    total = 0
    for tc_id in LOOPS_TC:
        mask = bundle.action_masks[tc_id]
        for action in mask.active_actions():
            total += len(mask.patterns_for_action(action, required_only=True))
    assert total == 54


def test_loops_mandatory_union_uses_only_catalog_patterns(bundle):
    catalog_ids = {p.id for p in bundle.exercise_patterns}
    used: set[str] = set()
    for tc_id in LOOPS_TC:
        mask = bundle.action_masks[tc_id]
        for action in mask.active_actions():
            used.update(mask.patterns_for_action(action, required_only=True))
    assert used.issubset(catalog_ids)
    assert len(used) <= len(catalog_ids)


def test_mastery_required_actions_not_all_six_for_loop_control(bundle):
    assert bundle.mastery_required_actions("loop_control") == (
        "recognize",
        "translate",
        "analyze",
        "debug",
        "implement",
    )
    assert bundle.mastery_required_actions("counted_loop") == (
        "recognize",
        "assemble",
        "translate",
        "analyze",
        "debug",
        "implement",
    )


def test_get_learning_concept_loops_detail(service):
    detail = service.get_learning_concept_detail("pascal", "loops")
    assert detail["learning_concept"]["id"] == "loops"
    tc_ids = [tc["id"] for tc in detail["technical_concepts"]]
    assert tc_ids == list(LOOPS_TC)


def test_get_required_patterns_counted_loop_translate(service):
    patterns = service.get_required_patterns("pascal", "counted_loop", "translate")
    assert patterns == ["tr_python_to_pascal_code", "tr_cpp_to_pascal_code"]


def test_invalid_language_raises():
    with pytest.raises(Exception):
        load_curriculum("rust")


def test_disabled_action_cannot_have_required_patterns_validation():
    bundle = load_curriculum("pascal", force=True)
    mask = bundle.action_masks["loop_control"]
    assert not mask.required_patterns_by_action.get("assemble")
