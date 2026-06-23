"""Fix exercise_pattern_id in pascal_showcase_all_specs.py per TC action masks."""

from __future__ import annotations

import re
from pathlib import Path

from application.curriculum.curriculum_service import CurriculumService
from application.curriculum.pascal.showcase.pascal_showcase_all_specs import all_pascal_showcase_specs

BUILDER_ACTION = {
    "pascal_io_program": "implement",
    "pascal_debug_starter": "debug",
    "translation_to_pascal": "translate",
    "block_reorder_pascal": "assemble",
}

PRIORITY_BY_ACTION: dict[str, list[str]] = {
    "implement": ["imp_io_tests_pascal", "imp_text_spec_to_pascal"],
    "debug": ["dbg_pascal_code_fix", "dbg_pascal_logic_fix", "dbg_transfer_syntax_fix"],
    "translate": [
        "tr_python_to_pascal_code",
        "tr_cpp_to_pascal_code",
        "tr_java_to_pascal_code",
        "tr_flowchart_to_pascal_code",
    ],
    "assemble": ["asm_blocks_to_code_pascal", "asm_flowchart_to_blocks"],
    "analyze": ["ana_pascal_code_predict_output", "ana_pascal_code_to_text"],
}

SPECS_PATH = Path(__file__).resolve().parents[1] / "application/curriculum/pascal_showcase_all_specs.py"


def pick_pattern(bundle, tc_id: str, action: str) -> str:
    mask = bundle.action_masks[tc_id]
    allowed = set(mask.patterns_for_action(action))
    for pid in PRIORITY_BY_ACTION[action]:
        if pid in allowed:
            return pid
    allowed_list = sorted(allowed)
    if not allowed_list:
        raise ValueError(f"No patterns for {tc_id}/{action}")
    return allowed_list[0]


def main() -> None:
    bundle = CurriculumService("pascal").get_bundle()
    text = SPECS_PATH.read_text(encoding="utf-8")
    changes: dict[str, str] = {}

    for specs in all_pascal_showcase_specs().values():
        for spec in specs:
            action = BUILDER_ACTION[spec.builder_key]
            correct = pick_pattern(bundle, spec.technical_concept_id, action)
            if spec.exercise_pattern_id != correct:
                changes[spec.slug] = correct

    for slug, new_pattern in sorted(changes.items()):
        block_pat = re.compile(
            rf'(slug="{re.escape(slug)}"[\s\S]*?)(exercise_pattern_id=")[^"]+(")',
            re.MULTILINE,
        )
        if block_pat.search(text):
            text = block_pat.sub(rf"\1\2{new_pattern}\3", text, count=1)
            print(f"replaced {slug} -> {new_pattern}")
            continue

        # Insert before test_cases for _io_spec without override
        insert_io = re.compile(
            rf'(slug="{re.escape(slug)}"[\s\S]{{0,500}}?technical_concept_id="[^"]+",\n)(\s*test_cases=)',
            re.MULTILINE,
        )
        if insert_io.search(text):
            text = insert_io.sub(
                rf'\1            exercise_pattern_id="{new_pattern}",\n\2',
                text,
                count=1,
            )
            print(f"inserted {slug} -> {new_pattern}")
            continue

        # Insert before closing paren for _debug_spec without override
        insert_dbg = re.compile(
            rf'(slug="{re.escape(slug)}"[\s\S]{{0,1200}}?reference_solution_pascal=[\s\S]*?\),\n)(\s*\),)',
            re.MULTILINE,
        )
        m = insert_dbg.search(text)
        if m:
            text = insert_dbg.sub(
                rf'\1            exercise_pattern_id="{new_pattern}",\n        ),',
                text,
                count=1,
            )
            print(f"inserted debug {slug} -> {new_pattern}")
        else:
            print(f"WARN: could not patch {slug} -> {new_pattern}")

    SPECS_PATH.write_text(text, encoding="utf-8")
    print(f"Done: {len(changes)} slugs updated")


if __name__ == "__main__":
    main()

