"""Unit tests for unified pedagogical task storage."""

from __future__ import annotations

from application.curriculum.mirror.pedagogical_task_store import (
    apply_learning_language_to_payload,
    apply_mirror_sibling_code_examples,
    canonical_pedagogical_slot_id,
    merge_language_track,
    populate_algo_v4_reference_examples,
    resolved_showcase,
    showcase_matches_collection,
)


def test_canonical_pedagogical_slot_id_maps_python_to_pascal():
    assert canonical_pedagogical_slot_id(slot_id="psk_01", language="pascal") == "psk_01"
    assert canonical_pedagogical_slot_id(slot_id="pyk_08", language="python") == "psk_09"
    assert canonical_pedagogical_slot_id(slot_id="pas_001", language="pascal") == "pas_001"


def test_showcase_matches_collection_for_synthesized_python_track():
    showcase = {
        "group": "pascal_curriculum_v311_functions",
        "collection_key": "functions",
        "slug": "pas_041",
        "slot_id": "pas_041",
        "target_language": "pascal",
        "pedagogical_slot_id": "algo_v4:041",
        "language_tracks": {
            "pascal": {
                "group": "pascal_curriculum_v311_functions",
                "collection_key": "functions",
                "slug": "pas_041",
                "slot_id": "pas_041",
                "target_language": "pascal",
            },
        },
    }
    assert showcase_matches_collection(
        showcase,
        language="python",
        collection_key="functions",
        group="python_curriculum_v311_functions",
    )


def test_resolved_showcase_overlays_language_track():
    showcase = {
        "pedagogical_slot_id": "psk_01",
        "slug": "psk_01",
        "target_language": "pascal",
        "group": "pascal_curriculum_v311_program_skeleton",
        "language_tracks": {
            "pascal": {"slug": "psk_01", "target_language": "pascal", "collection_key": "program_skeleton"},
            "python": {"slug": "pyk_01", "target_language": "python", "collection_key": "program_entry"},
        },
    }
    resolved = resolved_showcase(showcase, "python")
    assert resolved["slug"] == "pyk_01"
    assert resolved["target_language"] == "python"
    assert resolved["collection_key"] == "program_entry"


def test_apply_learning_language_to_payload_sets_task_language():
    payload = {
        "language": "pascal",
        "description": "Pascal goal",
        "code_examples": {
            "pascal": "program p; begin end.",
            "python": "def main(): pass",
            "curriculum_showcase": merge_language_track(
                {
                    "slug": "psk_01",
                    "target_language": "pascal",
                    "educational_goal": "Pascal goal",
                },
                {
                    "slug": "pyk_01",
                    "target_language": "python",
                    "collection_key": "program_entry",
                    "educational_goal": "Python goal",
                },
                "python",
            ),
        },
    }
    result = apply_learning_language_to_payload(payload, "python")
    assert result["language"] == "python"
    assert result["description"] == "Python goal"
    assert result["code_examples"]["curriculum_showcase"]["slug"] == "pyk_01"


def test_apply_mirror_sibling_code_examples_sets_pascal_fragment():
    showcase = merge_language_track(
        {"slug": "psk_09", "target_language": "pascal", "pedagogical_slot_id": "psk_09"},
        {"slug": "pyk_08", "target_language": "python", "pedagogical_slot_id": "psk_09"},
        "python",
    )
    payload = {
        "language": "python",
        "code_examples": {
            "python": "# py",
        },
    }
    result = apply_mirror_sibling_code_examples(payload, showcase, "python")
    assert "{ Однострочный }" in result["code_examples"]["pascal"]


def test_apply_mirror_sibling_code_examples_cpp_without_solution():
    showcase = {
        "slug": "java_008",
        "target_language": "java",
        "language_tracks": {
            "python": {"slug": "py_008", "target_language": "python", "collection_key": "algo_basics"},
            "java": {"slug": "java_008", "target_language": "java", "collection_key": "algo_basics"},
        },
    }
    payload = {"language": "java", "code_examples": {"python": "print(1)"}}
    result = apply_mirror_sibling_code_examples(payload, showcase, "cpp")
    assert result["language"] == "java"
    assert "code_examples" in result


def test_populate_algo_v4_reference_examples_fills_all_languages():
    showcase = {
        "slug": "pas_002",
        "slot_id": "pas_002",
        "target_language": "pascal",
        "language_tracks": {
            "pascal": {"slug": "pas_002"},
            "python": {"slug": "py_002"},
            "cpp": {"slug": "cpp_002"},
        },
    }
    payload = {"code_examples": {}}
    result = populate_algo_v4_reference_examples(payload, showcase, "cpp")
    examples = result["code_examples"]
    assert "readln" in examples["pascal"]
    assert "input" in examples["python"]
    assert "#include" in examples["cpp"]


def test_apply_learning_language_to_payload_uses_external_showcase():
    payload = {
        "language": "pascal",
        "description": "Pascal goal",
        "code_examples": {"pascal": "program p; begin end."},
    }
    showcase = merge_language_track(
        {"slug": "psk_01", "target_language": "pascal", "educational_goal": "Pascal goal"},
        {
            "slug": "pyk_01",
            "target_language": "python",
            "educational_goal": "Python goal",
        },
        "python",
    )
    result = apply_learning_language_to_payload(payload, "python", showcase=showcase)
    assert result["description"] == "Python goal"
    assert result["language"] == "python"


def test_sync_assembly_fields_for_language_copies_variant_to_root():
    from application.curriculum.mirror.pedagogical_task_store import sync_assembly_fields_for_language

    payload = {
        "language": "pascal",
        "template": "{0}\n\n{1}{",
        "blocks": ["import java.util.*;"],
        "language_variants": {
            "pascal": {
                "template": "{0}\n{1}\n{2}",
                "blocks": ["var n: integer;", "begin", "end."],
                "correct_order": [0, 1, 2],
            },
            "java": {
                "template": "{0}\n\n{1}{",
                "blocks": ["import java.util.*;"],
                "correct_order": [0],
            },
        },
    }
    result = sync_assembly_fields_for_language(payload, "pascal")
    assert result["template"] == "{0}\n{1}\n{2}"
    assert result["blocks"] == ["var n: integer;", "begin", "end."]
    assert result["correct_order"] == [0, 1, 2]
    assert result["language"] == "pascal"
