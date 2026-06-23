"""Display TC progress (tc_display_registry cards)."""

from application.learning.display_tc_progress_service import (
    build_display_tc_progress,
    build_display_tc_progress_by_language,
    enrich_code_examples_for_tc_progress,
    resolve_display_tc_ids_for_task,
    resolve_tc42_ids_for_task,
)


def test_resolve_display_tc_from_stored_expected_concepts():
    examples = {
        "curriculum_showcase": {
            "expected_concept_ids": ["assignment", "counted_loop", "simple_branch"],
        }
    }
    display_ids = resolve_display_tc_ids_for_task(examples)
    assert "tc_assignment" in display_ids
    assert "tc_loops" in display_ids
    assert "tc_conditionals" in display_ids


def test_task_counts_toward_multiple_display_tcs():
    examples = {
        "curriculum_showcase": {
            "expected_concept_ids": [
                "assignment",
                "counted_loop",
                "simple_branch",
                "indexed_sequence",
                "fold_aggregate",
            ],
        }
    }

    def get_examples(task_id: int):
        return examples if task_id == 1 else None

    rows = build_display_tc_progress(
        accessible_task_ids=[1, 2],
        solved_task_ids={1},
        get_code_examples=get_examples,
    )
    by_id = {row["id"]: row for row in rows}

    assert by_id["tc_assignment"]["total"] == 1
    assert by_id["tc_assignment"]["solved"] == 1
    assert by_id["tc_loops"]["total"] == 1
    assert by_id["tc_loops"]["solved"] == 1
    assert by_id["tc_aggregate"]["total"] == 1
    assert by_id["tc_aggregate"]["solved"] == 1


def test_progress_percent_is_solved_over_total_for_tc():
    task_a = {
        "curriculum_showcase": {"expected_concept_ids": ["counted_loop"]},
    }
    task_b = {
        "curriculum_showcase": {"expected_concept_ids": ["counted_loop"]},
    }
    task_c = {
        "curriculum_showcase": {"expected_concept_ids": ["counted_loop"]},
    }
    mapping = {1: task_a, 2: task_b, 3: task_c}

    rows = build_display_tc_progress(
        accessible_task_ids=[1, 2, 3],
        solved_task_ids={1},
        get_code_examples=lambda tid: mapping.get(tid),
    )
    loops = next(row for row in rows if row["id"] == "tc_loops")
    assert loops["total"] == 3
    assert loops["solved"] == 1
    assert loops["percent"] == 33.3


def test_registry_order_preserved():
    rows = build_display_tc_progress(
        accessible_task_ids=[],
        solved_task_ids=set(),
        get_code_examples=lambda _tid: None,
    )
    assert rows[0]["id"] == "tc_program_structure"
    assert rows[1]["id"] == "tc_variables_types"
    assert all(row["percent"] == 0.0 for row in rows)


def test_catalog_slot_fallback_resolves_tc42():
    examples = {
        "curriculum_showcase": {
            "slot_id": "py_001",
            "chapter_key": "program_entry",
        }
    }
    ids = resolve_tc42_ids_for_task(examples)
    assert ids


def test_algo_v128_slot_without_chapter_key_resolves_via_catalog():
    examples = {
        "curriculum_showcase": {
            "slot_id": "pas_001",
            "target_language": "pascal",
        }
    }
    ids = resolve_tc42_ids_for_task(examples)
    assert ids
    display_ids = resolve_display_tc_ids_for_task(examples)
    assert display_ids


def test_enrich_fills_expected_concepts_from_slot():
    raw = {"curriculum_showcase": {"slot_id": "py_002", "target_language": "python"}}
    enriched = enrich_code_examples_for_tc_progress(raw)
    showcase = enriched["curriculum_showcase"]
    assert showcase.get("expected_concept_ids") or resolve_tc42_ids_for_task(enriched)


def test_dedupes_mirror_rows_by_pedagogical_slot():
    shared_showcase = {
        "pedagogical_slot_id": "psk_01",
        "expected_concept_ids": ["counted_loop", "assignment"],
    }
    rows = build_display_tc_progress(
        accessible_task_ids=[101, 202],
        solved_task_ids={202},
        get_code_examples=lambda _tid: {"curriculum_showcase": dict(shared_showcase)},
    )
    loops = next(row for row in rows if row["id"] == "tc_loops")
    assert loops["total"] == 1
    assert loops["solved"] == 1
    console = next(row for row in rows if row["id"] == "tc_program_structure")
    assert console["total"] <= 1


def test_showcase_technical_concept_id_fallback():
    examples = {
        "curriculum_showcase": {
            "collection_key": "algo_basics",
            "technical_concept_id": "stdout_write",
        }
    }
    ids = resolve_tc42_ids_for_task(examples)
    assert "stdout_write" in ids
    display_ids = resolve_display_tc_ids_for_task(examples)
    assert "tc_console_io" in display_ids


def test_dedupes_algo_v4_pascal_and_python_rows():
    pascal = {
        "slot_id": "pas_001",
        "pedagogical_slot_id": "prc_001",
        "target_language": "pascal",
        "expected_concept_ids": ["console_output"],
    }
    python = {
        "slot_id": "py_001",
        "target_language": "python",
        "expected_concept_ids": ["console_output"],
    }
    mapping = {
        1: {"curriculum_showcase": pascal},
        129: {"curriculum_showcase": python},
    }
    rows = build_display_tc_progress(
        accessible_task_ids=[1, 129],
        solved_task_ids={129},
        get_code_examples=lambda tid: mapping.get(tid),
    )
    console = next(row for row in rows if row["id"] == "tc_console_io")
    assert console["total"] == 1
    assert console["solved"] == 1


def test_display_tc_progress_by_language_scopes_tracks_and_solves():
    pascal = {
        "slot_id": "shared_slot",
        "target_language": "pascal",
        "expected_concept_ids": ["counted_loop"],
    }
    python = {
        "slot_id": "shared_slot",
        "target_language": "python",
        "expected_concept_ids": ["counted_loop"],
    }
    cpp = {
        "slot_id": "cpp_only",
        "target_language": "cpp",
        "expected_concept_ids": ["counted_loop"],
    }
    mapping = {
        1: {"curriculum_showcase": pascal},
        2: {"curriculum_showcase": python},
        3: {"curriculum_showcase": cpp},
    }

    by_lang = build_display_tc_progress_by_language(
        languages=["pascal", "python", "cpp"],
        accessible_task_ids=[1, 2, 3],
        solved_task_ids_by_language={
            "pascal": {1},
            "python": set(),
            "cpp": {3},
        },
        task_languages=lambda tid: {
            1: ["pascal"],
            2: ["python"],
            3: ["cpp"],
        }[tid],
        get_code_examples=lambda tid: mapping.get(tid),
    )

    pascal_loops = next(row for row in by_lang["pascal"] if row["id"] == "tc_loops")
    python_loops = next(row for row in by_lang["python"] if row["id"] == "tc_loops")
    cpp_loops = next(row for row in by_lang["cpp"] if row["id"] == "tc_loops")

    assert pascal_loops["total"] == 1
    assert pascal_loops["solved"] == 1
    assert pascal_loops["percent"] == 100.0

    assert python_loops["total"] == 1
    assert python_loops["solved"] == 0
    assert python_loops["percent"] == 0.0

    assert cpp_loops["total"] == 1
    assert cpp_loops["solved"] == 1
