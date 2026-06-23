"""Tests for proactive MPLT scope on assembly gap templates."""

from __future__ import annotations

from application.curriculum.content.v4_assembly_builder import assembly_variant
from application.curriculum.display.proactive_scope import (
    proactive_pitfall_applies_to_student_workspace,
)
from application.curriculum.display.showcase_display import finalize_student_task_payload
from scripts.demo_fcc_afcc_content import T006_REF


def test_task_006_gap_template_puts_division_gap_on_pascal_output():
    variant = assembly_variant(
        "pascal",
        T006_REF["pascal"],
        task_format="сборка_фрагмента",
        pattern_id="task_006",
    )
    template = str(variant["template"])
    assert "total := {0}" in template
    assert "for i := {1} to {2}" in template
    assert "writeln(total {3} n)" in template
    assert variant["blocks"] == ["0", "0", "1", "n", "n - 1", "div", "/"]
    assert variant["correct_order"] == [0, 2, 3, 5]

    payload = {
        "type": "block_reorder",
        "primary_action": "assemble",
        "task_format": "сборка_фрагмента",
        "language": "pascal",
        "template": template,
    }
    assert proactive_pitfall_applies_to_student_workspace(
        payload,
        {"primary_action": "assemble", "task_format": "сборка_фрагмента"},
        pitfall_id="integer_division",
        target_language="pascal",
    ) is True


def test_task_006_gap_template_python_translation_pitfalls_only():
    variant = assembly_variant(
        "python",
        T006_REF["python"],
        task_format="сборка_фрагмента",
        pattern_id="task_006",
    )
    template = str(variant["template"])
    assert template.startswith("n = int(input())")
    assert "total = {0}" in template
    assert "for _ in range({1})" in template
    assert "print(total {2} n)" in template
    assert variant["blocks"] == ["0", "1", "n", "//", "/"]
    assert variant["correct_order"] == [0, 2, 3]
    assert "readln" not in variant["blocks"]


def test_finalize_task_006_assemble_cpp_to_pascal_shows_division_banner():
    variant = assembly_variant(
        "pascal",
        T006_REF["pascal"],
        task_format="сборка_фрагмента",
        pattern_id="task_006",
    )
    payload = finalize_student_task_payload(
        {
            "title": "Средняя загрузка сервера",
            "type": "block_reorder",
            "code_examples": {
                "teacher_assembly_override": True,
                "pascal": T006_REF["pascal"],
                "cpp": T006_REF["cpp"],
                "template": variant["template"],
                "blocks": variant["blocks"],
                "curriculum_showcase": {
                    "slot_pattern_id": "task_006",
                    "primary_action": "assemble",
                    "task_format": "сборка_фрагмента",
                    "target_language": "pascal",
                    "hints": [
                        "Сначала прочитайте n",
                        "Суммируйте все измерения",
                    ],
                },
            },
            "curriculum": {
                "slot_pattern_id": "task_006",
                "task_format": "сборка_фрагмента",
                "target_language": "pascal",
            },
        },
        source_language="cpp",
        target_language="pascal",
    )
    transfer = payload.get("transfer") or {}
    assert transfer.get("pitfall_id") == "integer_division"
    warning = str(transfer.get("reference_warning_ru") or transfer.get("proactive", {}).get("text") or "")
    assert warning.strip()


def test_implement_task_still_shows_integer_division_banner():
    payload = finalize_student_task_payload(
        {
            "title": "Средняя загрузка сервера",
            "primary_action": "implement",
            "code_examples": {
                "curriculum_showcase": {
                    "slot_pattern_id": "task_006",
                    "primary_action": "implement",
                    "target_language": "pascal",
                },
                "pascal": T006_REF["pascal"],
                "python": T006_REF["python"],
            },
            "curriculum": {"slot_pattern_id": "task_006", "target_language": "pascal"},
        },
        source_language="cpp",
        target_language="pascal",
    )
    transfer = payload.get("transfer") or {}
    warning = str(transfer.get("reference_warning_ru") or transfer.get("proactive", {}).get("text") or "")
    assert warning
    assert "div" in warning.lower() or "pascal" in warning.lower()
