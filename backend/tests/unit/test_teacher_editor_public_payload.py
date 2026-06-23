"""Teacher-edited tasks must win over catalog on final public payload."""

from __future__ import annotations

from types import SimpleNamespace

from application.tasks.services.teacher_editor_public_payload import (
    apply_teacher_editor_public_payload,
)


def test_apply_teacher_editor_public_payload_sets_type_code_and_action():
    row = SimpleNamespace(
        title="Teacher title",
        description="Teacher description",
        difficulty="medium",
        task_type="task_translate_full_program",
        test_cases=[{"name": "T1", "inputs": "", "output": "1"}],
        code_examples={
            "teacher_assembly_override": True,
            "python": "print('teacher')",
            "expected_concepts": {"python": ["tc_console_io"]},
            "curriculum_showcase": {
                "primary_action": "implement",
            },
        },
        block_reorder_task=None,
        translation_task=SimpleNamespace(
            source_language="python",
            source_code="print('teacher')",
        ),
    )

    payload = {
        "title": "Catalog title",
        "description": "Catalog description",
        "type": "task_build_from_blocks",
        "task_type": "task_build_from_blocks",
        "curriculum": {"action": "assemble"},
        "code_examples": {"python": "print('catalog')"},
    }

    result = apply_teacher_editor_public_payload(row, payload, learning_language="python")

    assert result["title"] == "Teacher title"
    assert result["description"] == "Teacher description"
    assert result["type"] == "task_translate_full_program"
    assert result["task_type"] == "task_translate_full_program"
    assert result["curriculum"]["action"] == "implement"
    assert result["source_code"] == "print('teacher')"
    assert result["code_examples"]["python"] == "print('teacher')"
    assert result["expected_concept_ids"]


def test_apply_teacher_editor_public_payload_preserves_debug_buggy_formatting():
    formatted_pascal = (
        "var n, i, sale, total: integer;\n"
        "begin\n"
        "  n = int(input());\n"
        "\n"
        "  total = 0;\n"
        "\n"
        "  print(total);\n"
        "end."
    )
    row = SimpleNamespace(
        title="Debug task",
        description="",
        difficulty="easy",
        task_type="task_translate_full_program",
        test_cases=[],
        code_examples={
            "teacher_assembly_override": True,
            "pascal": "var n: integer;\nbegin\nend.",
            "buggy_pascal": formatted_pascal,
            "curriculum_showcase": {
                "primary_action": "debug",
                "task_format": "исправление",
            },
        },
        block_reorder_task=None,
        translation_task=None,
    )
    payload = {
        "title": "Catalog",
        "curriculum": {"action": "debug"},
        "code_examples": {"pascal": "catalog"},
    }

    result = apply_teacher_editor_public_payload(row, payload, learning_language="pascal")

    assert result["curriculum"]["buggy_pascal"] == formatted_pascal
    assert result["code_examples"]["buggy_pascal"] == formatted_pascal
    assert result["code_examples"]["pascal"] == "var n: integer;\nbegin\nend."
    showcase = result["code_examples"]["curriculum_showcase"]
    assert "starter_pascal" not in showcase


def test_apply_teacher_editor_public_payload_debug_strips_block_reorder_surface():
    row = SimpleNamespace(
        title="Подсчёт положительных операций",
        description="",
        difficulty="easy",
        task_type="block_reorder",
        test_cases=[],
        code_examples={
            "teacher_assembly_override": True,
            "pascal": "var n, i, amount, count: integer;\nbegin\nend.",
            "buggy_pascal": "var n, i, amount, count: integer;\nbegin\n  count := 1;\nend.",
            "curriculum_showcase": {
                "primary_action": "debug",
                "task_format": "исправление",
            },
        },
        block_reorder_task=SimpleNamespace(
            language="pascal",
            template="count := {0};",
            blocks=["0", "1"],
            original_code="",
            correct_order=[0],
        ),
        translation_task=None,
    )
    payload = {
        "title": "Catalog",
        "type": "block_reorder",
        "task_type": "block_reorder",
        "blocks": ["0", "1"],
        "template": "count := {0};",
        "code_examples": {},
    }

    result = apply_teacher_editor_public_payload(row, payload, learning_language="pascal")

    assert result["type"] == "algorithm"
    assert result["task_type"] == "algorithm"
    assert "blocks" not in result
    assert "template" not in result
    assert result["code_examples"]["buggy_pascal"].startswith("var n")


def test_apply_teacher_editor_public_payload_migrates_legacy_debug_starter():
    formatted_pascal = "begin\n  writeln(1);\nend."
    row = SimpleNamespace(
        title="Debug task",
        description="",
        difficulty="easy",
        task_type="task_translate_full_program",
        test_cases=[],
        code_examples={
            "teacher_assembly_override": True,
            "pascal": "begin\nend.",
            "curriculum_showcase": {
                "primary_action": "debug",
                "task_format": "исправление",
                "starter_pascal": formatted_pascal,
            },
        },
        block_reorder_task=None,
        translation_task=None,
    )
    payload = {
        "title": "Catalog",
        "curriculum": {"action": "debug"},
        "code_examples": {},
    }

    result = apply_teacher_editor_public_payload(row, payload, learning_language="pascal")

    assert result["code_examples"]["buggy_pascal"] == formatted_pascal
    assert "starter_pascal" not in result["code_examples"]["curriculum_showcase"]
