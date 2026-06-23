"""Stages 14–16: per-language expected concepts and transfer meta."""

from __future__ import annotations

from application.curriculum.content.algo_syntax_showcase_meta import (
    attach_expected_concepts_to_extra,
    enrich_student_expected_concepts,
    expected_concept_ids_by_language,
    resolve_source_language,
    transfer_meta_for_language_pair,
)
from application.curriculum.display.pitfall_catalog import (
    build_pitfall_payload_for_languages,
    get_pitfall,
    pitfall_applies_to_language_pair,
)
from application.curriculum.display.showcase_display import sanitize_public_task_payload


def test_pas_003_resolves_task_005_not_task_003():
    by_lang = expected_concept_ids_by_language("pas_003", slot_pattern_id="task_005")
    assert "cpp" in by_lang
    assert len(by_lang["cpp"]) >= 4


def test_pas_003_v128_slot_maps_to_task_005():
    by_lang = expected_concept_ids_by_language("pas_003", slot_pattern_id=None)
    explicit = expected_concept_ids_by_language("pas_003", slot_pattern_id="task_005")
    assert by_lang == explicit
    assert "cpp" in by_lang
    assert len(by_lang["cpp"]) >= 4


def test_task_002_python_includes_search_find_chip():
    from application.curriculum.content.algo_syntax_task_extra import algo_expected_concepts
    from application.curriculum.validation.expected_concept_checker import (
        analyze_expected_concepts,
        build_technical_expected_concept_cards,
    )

    ids = algo_expected_concepts("pas_001", "python", slot_pattern_id="task_002")
    assert "search_find" in ids
    cards = build_technical_expected_concept_cards(ids, learning_language="python")
    assert any(c.get("display_id") == "tc_search" for c in cards)

    code = """n, target = map(int, input().split())
position = 0
for i in range(1, n + 1):
    code = int(input())
    if code == target and position == 0:
        position = i
print(position)"""
    scan = analyze_expected_concepts(code, language="python", concept_ids=ids)
    search = next(item for item in scan if item.id == "search_find")
    assert search.detected is True


def test_task_129_features_keep_loop_chip_despite_short_reference():
    from application.curriculum.content.algo_syntax_task_extra import algo_expected_concepts

    ids = algo_expected_concepts("pas_007", "python", slot_pattern_id="task_129")
    assert "loop" in ids


def test_pas_004_v128_slot_maps_to_task_001():
    from application.curriculum.content.algo_syntax_task_extra import resolve_slot_pattern_key

    assert resolve_slot_pattern_key("pas_004") == "task_001"


def test_task_006_python_expected_uses_counted_loop_not_collection_iteration():
    from application.curriculum.content.algo_syntax_task_extra import algo_expected_concepts
    from application.curriculum.validation.expected_concept_checker import analyze_expected_concepts

    ids = algo_expected_concepts("pas_003", "python", slot_pattern_id="task_006")
    assert "loop" in ids
    assert "collection_iteration" not in ids

    code = (
        "n = int(input())\n"
        "total = 0\n"
        "for _ in range(n):\n"
        "    load = int(input())\n"
        "    total += load\n"
        "print(total // n)"
    )
    scan = analyze_expected_concepts(code, language="python", concept_ids=ids)
    loops = next(item for item in scan if item.id == "loop")
    assert loops.detected is True


def test_task_001_python_expected_loop_detected_in_range_for():
    from application.curriculum.content.algo_syntax_task_extra import algo_expected_concepts
    from application.curriculum.validation.expected_concept_checker import analyze_expected_concepts

    ids = algo_expected_concepts("pas_004", "python", slot_pattern_id="task_001")
    assert "loop" in ids
    assert "collection_iteration" not in ids
    assert "indexed_sequence" not in ids

    code = (
        "n = int(input())\n"
        "best = None\n"
        "for _ in range(n):\n"
        "    score = int(input())\n"
        "    if best is None or score > best:\n"
        "        best = score\n"
        "print(best)"
    )
    scan = analyze_expected_concepts(code, language="python", concept_ids=ids)
    assert all(item.detected for item in scan if item.id in {"loop", "conditional"})


def test_task_005_no_chapter_hint_tcc():
    meta = transfer_meta_for_language_pair(
        "task_005",
        source_language="pascal",
        target_language="cpp",
    )
    assert meta.get("transfer_type") == "TCC"
    assert not meta.get("reference_warning_ru")
    assert meta["proactive"]["text"] is None


def test_input_line_model_applies_pascal_to_cpp_with_pair_hint():
    spec = get_pitfall("input_line_model")
    assert spec
    assert pitfall_applies_to_language_pair(
        spec,
        source_language="pascal",
        target_language="cpp",
    )
    payload = build_pitfall_payload_for_languages(
        "input_line_model",
        source_language="cpp",
        target_language="java",
    )
    assert payload.get("reference_warning_ru")
    assert "Scanner" in payload["reference_warning_ru"] or "cin" in payload["reference_warning_ru"].lower()


def test_attach_expected_concepts_by_language():
    extra = attach_expected_concepts_to_extra(
        {},
        slot_id="pas_003",
        slot_pattern_id="task_005",
    )
    assert extra["slot_pattern_id"] == "task_005"
    assert isinstance(extra.get("expected_concepts"), dict)
    assert len(extra["expected_concepts"].get("cpp") or []) >= 4


def test_enrich_student_payload_technical_chips():
    payload = enrich_student_expected_concepts(
        {
            "id": 3,
            "curriculum": {"slot_id": "pas_003", "target_language": "cpp"},
            "code_examples": {
                "pascal": "program T; begin end.",
                "curriculum_showcase": {
                    "known_language_variants": {
                        "pascal": {"source_code": "program T; begin end."},
                    },
                },
            },
        },
        pattern_key="task_005",
        slot_id="pas_003",
        target_language="cpp",
        slot_pattern_id="task_005",
    )
    cards = payload["curriculum"]["expected_concepts"]
    assert len(cards) >= 4
    assert all(not str(c["id"]).startswith("tc_") for c in cards)
    assert payload["curriculum"].get("expected_concepts_mode") == "technical"
    program = next(c for c in cards if c.get("display_id") == "tc_program_structure")
    assert program.get("examples_by_language", {}).get("cpp")
    assert program.get("in_proactive_scope") is False
    assert not program.get("transfer_hint_ru")


def test_technical_cards_dedupe_display_tc():
    from application.curriculum.validation.expected_concept_checker import (
        build_technical_expected_concept_cards,
    )

    cards = build_technical_expected_concept_cards(
        ["program_entry", "main_entry"],
        learning_language="cpp",
        source_language="pascal",
    )
    assert len(cards) == 1
    assert cards[0]["display_id"] == "tc_program_structure"


def test_sanitize_pas_003_cpp_no_python_pascal_warning():
    payload = sanitize_public_task_payload(
        {
            "id": 3,
            "title": "[1. Базовый синтаксис] Сумма выручки",
            "code_examples": {
                "pascal": "program T; begin end.",
                "curriculum_showcase": {
                    "slot_id": "pas_003",
                    "slot_pattern_id": "task_005",
                    "exercise_pattern_id": "task_005",
                    "target_language": "cpp",
                    "technical_concept_id": "program_entry",
                    "known_language_variants": {
                        "pascal": {"source_code": "program T; begin end."},
                    },
                },
            },
            "curriculum": {"slot_id": "pas_003", "target_language": "cpp"},
        }
    )
    transfer = (payload.get("curriculum") or {}).get("transfer") or payload.get("transfer") or {}
    warning = str(transfer.get("reference_warning_ru") or "")
    assert not warning.startswith("Модель ввода одной строки в Python и Pascal")
    concepts = payload["curriculum"]["expected_concepts"]
    assert len(concepts) >= 4
    assert all(not str(c["id"]).startswith("tc_") for c in concepts)


def test_integer_division_warning_python_to_pascal_and_cpp_to_python():
    meta_py_pas = transfer_meta_for_language_pair(
        "task_006",
        source_language="python",
        target_language="pascal",
    )
    assert meta_py_pas.get("pitfall_id") == "integer_division"
    meta_cpp_py = transfer_meta_for_language_pair(
        "task_006",
        source_language="cpp",
        target_language="python",
    )
    assert meta_cpp_py.get("pitfall_id") == "integer_division"
    assert "reference_warning_ru" in meta_cpp_py
    blocked = transfer_meta_for_language_pair(
        "task_006",
        source_language="pascal",
        target_language="cpp",
    )
    assert blocked.get("pitfall_id") == "integer_division"
    assert "reference_warning_ru" in blocked
    assert "div/mod" in blocked["reference_warning_ru"] or "C++" in blocked["reference_warning_ru"]


def test_sanitize_pas_005_teacher_attach_path_cpp_to_java():
    from application.tasks.services.teacher_editor_public_payload import (
        apply_teacher_editor_public_payload,
    )
    from application.curriculum.display.showcase_display import finalize_student_task_payload

    class Row:
        title = "[1. Базовый синтаксис] Подсчёт положительных операций"
        description = "x"
        difficulty = "easy"
        task_type = "debug_code"
        test_cases = []
        code_examples = {
            "curriculum_showcase": {
                "slot_id": "pas_005",
                "target_language": "java",
                "technical_concept_id": "tc_console_io",
                "expected_concept_ids": ["tc_console_io"],
                "known_language_variants": {
                    "cpp": {"source_code": "#include <iostream>"},
                    "java": {"source_code": "class Main {}"},
                },
            },
        }

    payload = finalize_student_task_payload(
        apply_teacher_editor_public_payload(
            Row(),
            {
                "title": Row.title,
                "code_examples": Row.code_examples,
                "curriculum": {"slot_id": "pas_005", "target_language": "java"},
            },
            learning_language="java",
        )
    )
    assert payload["title"] == "Подсчёт положительных операций"
    concepts = (payload.get("curriculum") or {}).get("expected_concepts") or []
    assert len(concepts) >= 6
    assert all(str(c.get("name_ru") or "").strip() for c in concepts)
    assert all(not str(c.get("name_ru")).startswith("tc_") for c in concepts)
    transfer = payload.get("transfer") or (payload.get("curriculum") or {}).get("transfer") or {}
    assert transfer.get("transfer_type") == "TCC"
    assert transfer.get("debug_id") == "filter_positive"
    assert transfer.get("pitfall_id") is None
    assert not transfer.get("reference_warning_ru")
    assert transfer.get("proactive", {}).get("text") is None


def test_finalize_task_006_cpp_to_python_proactive():
    from application.curriculum.display.showcase_display import finalize_student_task_payload

    payload = finalize_student_task_payload(
        {
            "title": "Средняя загрузка сервера",
            "code_examples": {
                "teacher_assembly_override": True,
                "curriculum_showcase": {
                    "slot_pattern_id": "task_006",
                    "primary_action": "assemble",
                    "target_language": "python",
                    "expected_concepts": {
                        "python": ["tc_program_structure", "tc_console_io", "tc_arithmetic"],
                    },
                },
                "expected_concepts": {
                    "python": ["tc_program_structure", "tc_console_io", "tc_arithmetic"],
                },
                "cpp": "int main() { return 0; }",
                "python": "print(1)",
            },
            "curriculum": {"slot_pattern_id": "task_006", "target_language": "python"},
        },
        source_language="cpp",
        target_language="python",
    )
    transfer = payload.get("transfer") or {}
    warning = str(transfer.get("reference_warning_ru") or transfer.get("proactive", {}).get("text") or "")
    assert "Python" in warning
    assert "C++" in warning or "комментар" in warning.lower()
    assert "Pascal" not in warning
    concepts = payload.get("expected_concepts") or []
    assert concepts
    assert all(str(c.get("name_ru") or "").strip() for c in concepts)
    assert "tc_" not in str(concepts[0].get("name_ru"))


def test_finalize_task_006_demo_expected_concepts_include_arithmetic_and_loops():
    from application.curriculum.display.showcase_display import finalize_student_task_payload
    from scripts.demo_fcc_afcc_content import T006_CONCEPTS, T006_REF

    payload = finalize_student_task_payload(
        {
            "title": "Средняя загрузка сервера",
            "type": "block_reorder",
            "code_examples": {
                "teacher_assembly_override": True,
                "java": T006_REF["java"],
                "python": T006_REF["python"],
                "expected_concepts": {lang: list(T006_CONCEPTS) for lang in ("pascal", "python", "cpp", "csharp", "java")},
                "curriculum_showcase": {
                    "slot_pattern_id": "task_006",
                    "slot_id": "pas_004",
                    "primary_action": "assemble",
                    "task_format": "сборка_фрагмента",
                    "expected_concept_ids": list(T006_CONCEPTS),
                    "expected_concepts": {
                        lang: list(T006_CONCEPTS) for lang in ("pascal", "python", "cpp", "csharp", "java")
                    },
                },
            },
            "curriculum": {"slot_pattern_id": "task_006", "target_language": "java"},
        },
        source_language="python",
        target_language="java",
    )
    names = [str(c.get("name_ru") or "") for c in (payload.get("expected_concepts") or [])]
    assert len(names) >= 5
    assert "Структура программы" in names
    assert "Ввод и вывод (консоль)" in names
    assert any("Арифмет" in name for name in names)
    assert any("Цикл" in name for name in names)


def test_finalize_same_language_pair_has_no_transfer_banner():
    from application.curriculum.display.showcase_display import finalize_student_task_payload

    payload = finalize_student_task_payload(
        {
            "title": "Средняя загрузка сервера",
            "code_examples": {
                "teacher_assembly_override": True,
                "curriculum_showcase": {
                    "slot_pattern_id": "task_006",
                    "target_language": "cpp",
                },
                "cpp": "int main() { return 0; }",
            },
            "curriculum": {"slot_pattern_id": "task_006", "target_language": "cpp"},
        },
        source_language="cpp",
        target_language="cpp",
    )
    transfer = payload.get("transfer") or {}
    assert not str(transfer.get("reference_warning_ru") or "").strip()
    assert not str(transfer.get("proactive", {}).get("text") or "").strip()


def test_sanitize_pas_004_cpp_to_python_transfer_and_title():
    payload = sanitize_public_task_payload(
        {
            "id": 4,
            "title": "[1. Базовый синтаксис] Средняя загрузка сервера",
            "code_examples": {
                "cpp": "#include <iostream>",
                "python": "n = int(input())",
                "curriculum_showcase": {
                    "slot_id": "pas_004",
                    "target_language": "python",
                    "technical_concept_id": "console_io",
                    "known_language_variants": {
                        "cpp": {"source_code": "#include <iostream>"},
                    },
                },
            },
            "curriculum": {"slot_id": "pas_004", "target_language": "python"},
        }
    )
    assert payload["title"] == "Средняя загрузка сервера"
    transfer = (payload.get("curriculum") or {}).get("transfer") or payload.get("transfer") or {}
    warning = str(transfer.get("reference_warning_ru") or transfer.get("hint_ru") or "")
    assert warning
    concepts = payload["curriculum"]["expected_concepts"]
    assert len(concepts) >= 4
    assert all(not str(c["id"]).startswith("tc_") for c in concepts)


def test_resolve_source_language_ignores_catalog_cpp_for_pascal_target():
    source = resolve_source_language(
        {
            "code_examples": {
                "pascal": "program T; begin end.",
                "cpp": "#include <iostream>",
                "python": "print(1)",
            }
        },
        {},
        target_language="pascal",
    )
    assert source == "python"


def test_task_003_cpp_to_java_input_line_proactive():
    meta = transfer_meta_for_language_pair(
        "task_003",
        source_language="cpp",
        target_language="java",
    )
    warning = str(meta.get("reference_warning_ru") or "")
    assert warning
    assert "Scanner" in warning or "readLine" in warning or "cin" in warning.lower()


def test_finalize_pas_007_java_popover_examples_language():
    from application.curriculum.display.showcase_display import finalize_student_task_payload

    payload = finalize_student_task_payload(
        {
            "title": "Минимальная задержка сервера",
            "code_examples": {
                "curriculum_showcase": {
                    "slot_id": "pas_007",
                    "target_language": "java",
                    "known_language_variants": {
                        "cpp": {"source_code": "#include <iostream>"},
                        "java": {"source_code": "class Main {}"},
                    },
                },
            },
            "curriculum": {"slot_id": "pas_007", "target_language": "java"},
        }
    )
    cards = (payload.get("curriculum") or {}).get("expected_concepts") or []
    io_card = next((c for c in cards if c.get("display_id") == "tc_console_io" or "stdin" in str(c.get("id"))), None)
    if io_card is None and cards:
        io_card = cards[0]
    assert io_card is not None
    examples = io_card.get("examples_by_language") or {}
    java_rows = examples.get("java") or []
    assert java_rows
    assert "Scanner" in str(java_rows[0].get("code") or "") or "System.out" in str(java_rows[0].get("code") or "")

