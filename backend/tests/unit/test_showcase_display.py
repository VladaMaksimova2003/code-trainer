"""Tests — student-facing showcase title sanitization."""

from __future__ import annotations

from application.curriculum.display.showcase_display import (
    _extract_showcase_student_fields,
    _merge_starter_fields_into_curriculum,
    enrich_pascal_showcase_hints,
    resolve_showcase_technical_concept_id,
    sanitize_public_task_payload,
    sanitize_student_code_examples,
    strip_showcase_title_prefix,
)


def test_resolve_showcase_technical_concept_id_maps_legacy_imports():
    order = ("simple_branch", "multi_branch")
    assert resolve_showcase_technical_concept_id("program_entry", order) == "simple_branch"
    assert resolve_showcase_technical_concept_id("simple_branch", order) == "simple_branch"
    assert resolve_showcase_technical_concept_id(None, order) == "simple_branch"


def test_strip_showcase_title_prefix():
    assert (
        strip_showcase_title_prefix("[Pascal Loops Showcase] Цикл for: перевод с Python на Pascal")
        == "Цикл for: перевод с Python на Pascal"
    )
    assert (
        strip_showcase_title_prefix("[Pascal v3.1.1: 1. Каркас program] Каркас program ... begin ... end.")
        == "Каркас program ... begin ... end."
    )
    assert (
        strip_showcase_title_prefix("[10. Словари и key-value структуры] Итоговая: анализ текста через словарь")
        == "Итоговая: анализ текста через словарь"
    )


def test_sanitize_public_task_payload_strips_showcase_metadata():
    payload = sanitize_public_task_payload(
        {
            "id": 1,
            "title": "[Pascal Loops Showcase] Цикл for: перевод с Python на Pascal",
            "code_examples": {
                "python": "print(1)",
                "curriculum_showcase": {"group": "pascal_curriculum_loops_v1", "slug": "x"},
            },
        }
    )
    assert payload["title"] == "Цикл for: перевод с Python на Pascal"
    assert "curriculum_showcase" not in payload["code_examples"]


def test_sanitize_public_task_payload_uses_explicit_expected_concept_ids():
    payload = sanitize_public_task_payload(
        {
            "id": 113,
            "title": "[Pascal v3.1.1] Пустой оператор begin … end",
            "code_examples": {
                "curriculum_showcase": {
                    "slug": "psk_12",
                    "target_language": "pascal",
                    "technical_concept_id": "program_entry",
                    "pascal_features": "begin; end",
                    "expected_concept_ids": ["block_scope"],
                },
            },
            "curriculum": {"language": "pascal", "technical_concept_id": "program_entry"},
        }
    )
    assert payload["expected_concept_ids"] == ["tc_program_structure"]
    assert [c["id"] for c in payload["expected_concepts"]] == ["tc_program_structure"]
    assert payload["curriculum"]["expected_concept_ids"] == ["tc_program_structure"]


def test_sanitize_public_task_payload_exposes_expected_concepts():
    payload = sanitize_public_task_payload(
        {
            "id": 8,
            "title": "[Pascal Conditions Showcase] Условие if",
            "code_examples": {
                "python": "if x > 0: print(1)",
                "curriculum_showcase": {
                    "slug": "simple_branch_tr_python",
                    "target_language": "pascal",
                    "technical_concept_id": "simple_branch",
                    "known_language_variants": {
                        "python": {"source_code": "if x > 0: print(1)"},
                    },
                    "expected_output": "42",
                    "primary_action": "analyze",
                },
            },
            "curriculum": {"language": "pascal"},
        }
    )
    assert payload["language"] == "pascal"
    assert payload["expected_concepts"]
    assert payload["expected_concept_ids"]
    assert "Условия и ветвление" in [c["name_ru"] for c in payload["expected_concepts"]]
    assert payload["curriculum"]["expected_concepts"]
    assert "curriculum_showcase" not in payload["code_examples"]


def test_sanitize_public_task_payload_merges_known_language_variants():
    payload = sanitize_public_task_payload(
        {
            "id": 2,
            "title": "[Pascal Showcase] Перевод",
            "code_examples": {
                "curriculum_showcase": {
                    "target_language": "pascal",
                    "primary_action": "translate",
                    "known_language_variants": {
                        "python": {"source_code": "print(42)"},
                        "cpp": {"source_code": "int main(){ return 0; }"},
                    },
                },
            },
            "curriculum": {"language": "pascal"},
        }
    )
    assert payload["code_examples"]["python"] == "print(42)"
    assert payload["code_examples"]["cpp"] == "int main(){ return 0; }"
    assert "curriculum_showcase" not in payload["code_examples"]


def test_sanitize_public_task_payload_refreshes_python_demo_known_variants():
    payload = sanitize_public_task_payload(
        {
            "id": 99,
            "title": "[Python v1: 1. Базовая программа] Посчитать сумму",
            "code_examples": {
                "curriculum_showcase": {
                    "slot_id": "py_003",
                    "slug": "py_003",
                    "target_language": "python",
                    "primary_action": "implement",
                    "known_language_variants": {
                        "pascal": {"source_code": "writeln('demo');"},
                        "cpp": {"source_code": 'std::cout << "demo";'},
                        "java": {"source_code": 'System.out.println("demo");'},
                        "csharp": {"source_code": 'Console.WriteLine("demo");'},
                        "python": {"source_code": "a = 7\nb = 5\ns = a + b\nprint(s)"},
                    },
                },
            },
            "curriculum": {"language": "python"},
        }
    )
    assert payload["code_examples"]["pascal"]
    assert payload["code_examples"]["cpp"]


def test_sanitize_public_task_payload_preserves_block_reorder_fields_on_empty_catalog_refresh():
    payload = sanitize_public_task_payload(
        {
            "id": 210,
            "type": "blocks",
            "blocks": ["for i:=1 to n do", "readln(a[i])", "write(a[i])"],
            "template": "for i:=1 to n do\n  readln(a[i]);",
            "code_examples": {
                "curriculum_showcase": {
                    "slot_id": "pas_026",
                    "task_format": "сборка_фрагмента",
                    "primary_action": "assemble",
                    "educational_goal": "Даны n, k и массив из n чисел.",
                },
            },
        }
    )
    assert len(payload["blocks"]) == 3
    assert payload["template"]


def test_sanitize_public_task_payload_refreshes_legacy_pascal_slot_description():
    payload = sanitize_public_task_payload(
        {
            "id": 214,
            "type": "blocks",
            "blocks": ["Copy", "sub", "result", "writeln(result)"],
            "template": "program Demo;\nvar s, sub, result: string;\nbegin\n  readln(s);\n  {0}\n  writeln({1});\nend.",
            "description": "Старое условие",
            "code_examples": {
                "curriculum_showcase": {
                    "slot_id": "str_07",
                    "task_format": "сборка_фрагмента",
                    "primary_action": "assemble",
                },
            },
        }
    )
    assert payload["description"] == "Старое условие"
    assert payload["blocks"]
    assert sanitize_student_code_examples(None) is None


def test_sanitize_public_task_payload_syncs_stale_python_v4_expected_concepts():
    payload = sanitize_public_task_payload(
        {
            "id": 200,
            "title": "[Python v1: 3. Условия] Сравнение",
            "code_examples": {
                "python": "age = int(input())\nprint(age == 18)",
                "curriculum_showcase": {
                    "slot_id": "py_025",
                    "slug": "py_025",
                    "target_language": "python",
                    "technical_concept_id": "simple_branch",
                    "primary_action": "implement",
                    "test_cases": [{"input": "18\n", "output": "True\n"}],
                    "expected_concept_ids": ["program_entry"],
                    "known_language_variants": {
                        "python": {"source_code": "age = int(input())\nprint(age == 18)"},
                        "pascal": {"source_code": "var age: integer;\nbegin\n  readln(age);\n  writeln(age = 18);\nend."},
                    },
                },
            },
            "curriculum": {"language": "python", "technical_concept_id": "simple_branch"},
        }
    )
    assert payload["expected_concept_ids"]
    assert payload["curriculum"].get("expected_concepts_mode") == "technical"
    assert len(payload["expected_concept_ids"]) > 1
    assert all(not str(item).startswith("tc_") for item in payload["expected_concept_ids"])
    assert all(not str(c["id"]).startswith("tc_") for c in payload["expected_concepts"])
    names = [c["name_ru"] for c in payload["expected_concepts"]]
    assert names


def test_enrich_pascal_sets_learning_language():
    payload = enrich_pascal_showcase_hints(
        {
            "language": "python",
            "code_examples": {"python": "x=1"},
            "curriculum": {
                "language": "pascal",
                "technical_concept_id": "assignment",
            },
        }
    )
    assert payload["language"] == "pascal"
    assert payload["expected_concept_ids"]


def test_enrich_pascal_does_not_emit_concept_visualization():
    payload = enrich_pascal_showcase_hints(
        {
            "title": "[Pascal Conditions Showcase] Условие if",
            "code_examples": {
                "python": "if n > 0: print('pos')",
                "curriculum_showcase": {
                    "target_language": "pascal",
                    "technical_concept_id": "simple_branch",
                },
            },
            "curriculum": {"language": "pascal", "technical_concept_id": "simple_branch"},
        }
    )
    assert "concept_visualization" not in payload
    assert "concept_visualization" not in (payload.get("curriculum") or {})


def test_extract_showcase_student_fields_includes_cpp_starter():
    formatted_cpp = (
        "#include <iostream>\n"
        "\n"
        "int main() {\n"
        "    return 0;\n"
        "}\n"
    )
    fields = _extract_showcase_student_fields(
        {
            "csharp": "using System;",
            "curriculum_showcase": {
                "slot_id": "cpp_005",
                "target_language": "cpp",
                "starter_cpp": formatted_cpp,
            },
        }
    )
    assert fields["starter_cpp"] == formatted_cpp

    curriculum = _merge_starter_fields_into_curriculum({"language": "cpp"}, fields)
    assert curriculum["starter_cpp"] == formatted_cpp


def test_sanitize_public_task_payload_attaches_transfer_meta():
    payload = sanitize_public_task_payload(
        {
            "id": 12,
            "title": "Debug: ветвление",
            "curriculum": {"slot_id": "pas_012", "language": "pascal"},
            "code_examples": {
                "curriculum_showcase": {
                    "slot_id": "pas_012",
                    "slot_pattern_id": "task_012",
                    "target_language": "pascal",
                },
            },
        }
    )
    transfer = payload.get("transfer") or (payload.get("curriculum") or {}).get("transfer")
    assert transfer
    assert transfer.get("transfer_type") == "TCC"
    assert transfer.get("debug_id") == "branch_logic"
    assert transfer.get("pitfall_id") is None
    assert not transfer.get("reference_warning_ru")
    assert transfer.get("proactive", {}).get("text") is None


def test_finalize_promotes_hints_and_post_solve_from_code_examples():
    from application.curriculum.display.showcase_display import finalize_student_task_payload

    payload = finalize_student_task_payload(
        {
            "id": 5,
            "title": "Подсчёт положительных операций",
            "curriculum": {
                "slot_id": "pas_005",
                "slot_pattern_id": "task_004",
                "language": "pascal",
                "action": "debug",
            },
            "code_examples": {
                "hints": ["hint one", "hint two"],
                "post_solve_explanation": "post solve text",
                "curriculum_showcase": {
                    "slot_id": "pas_005",
                    "slot_pattern_id": "task_004",
                    "primary_action": "debug",
                    "task_format": "исправление",
                },
            },
        }
    )
    assert payload["hints"] == ["hint one", "hint two"]
    assert payload["post_solve_explanation"] == "post solve text"
    assert payload["curriculum"]["hints"] == ["hint one", "hint two"]
    assert payload["curriculum"]["post_solve_explanation"] == "post solve text"

