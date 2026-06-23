"""Tests for showcase pattern resolution and analyze action labels."""

from __future__ import annotations

from dataclasses import replace

from application.curriculum.pascal.legacy.conditions.conditions_showcase_data import conditions_showcase_specs
from application.curriculum.display.curriculum_labels import (
    ACTION_DESCRIPTIONS_RU,
    ACTION_LABELS,
    ACTION_SKILL_LABELS_RU,
    build_curriculum_display,
)
from application.curriculum.pascal.legacy.loops.loops_showcase_data import loops_showcase_specs
from application.curriculum.pascal.showcase.pascal_showcase_core import (
    PascalShowcaseTaskSpec,
    resolve_showcase_exercise_pattern,
    with_resolved_pattern,
)


def _spec(slug: str, specs):
    return next(item for item in specs if item.slug == slug)


def test_resolve_keeps_valid_analyze_pattern_for_conditions():
    raw = _spec("conditional_expression_analyze", conditions_showcase_specs())
    assert resolve_showcase_exercise_pattern(raw) == "ana_pascal_code_predict_output"
    resolved = with_resolved_pattern(raw)
    assert resolved.exercise_pattern_id == "ana_pascal_code_predict_output"


def test_resolve_keeps_valid_analyze_pattern_for_loops():
    raw = _spec("post_condition_analyze_output", loops_showcase_specs())
    assert resolve_showcase_exercise_pattern(raw) == "ana_pascal_code_predict_output"
    resolved = with_resolved_pattern(raw)
    assert resolved.exercise_pattern_id == "ana_pascal_code_predict_output"


def test_analyze_student_labels():
    display = build_curriculum_display(
        language="pascal",
        learning_concept_id="loops",
        technical_concept_id="post_condition_loop",
        action="analyze",
        exercise_pattern_id="ana_pascal_code_predict_output",
    )
    assert ACTION_LABELS["analyze"] == "Разобрать код"
    assert ACTION_SKILL_LABELS_RU["analyze"] == "Предсказать результат"
    assert ACTION_DESCRIPTIONS_RU["analyze"] == "Что выведет программа?"
    assert display["action_label"] == "Разобрать код"
    assert display["action_skill_label"] == "Предсказать результат"
    assert display["instruction_ru"] == "Что выведет программа?"
    assert "theme_name_ru" in display
    assert "subtopic_name_ru" in display
    assert "skill_line_ru" not in display
    assert "format_line_ru" not in display


def test_resolve_falls_back_to_builder_action_when_pattern_invalid():
    raw = replace(
        _spec("counted_loop_tr_python", loops_showcase_specs()),
        exercise_pattern_id="totally_invalid_pattern_id",
    )
    assert resolve_showcase_exercise_pattern(raw) == "tr_python_to_pascal_code"


