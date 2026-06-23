#!/usr/bin/env python3
"""One-off: mirror pascal showcase modules to python."""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BASE_P = REPO / "application/curriculum/pascal/showcase"
BASE_PY = REPO / "application/curriculum/python/showcase"

FILES = [
    "pascal_showcase_core.py",
    "pascal_showcase_next.py",
    "pascal_showcase_student.py",
]

REPLACEMENTS = [
    ("application.curriculum.pascal", "application.curriculum.python"),
    ("PascalShowcaseTaskSpec", "PythonShowcaseTaskSpec"),
    ("PascalV311Collection", "PythonV311Collection"),
    ("pascal_v311_registry", "python_v311_registry"),
    ("pascal_v311_showcase_all_specs", "python_v311_showcase_all_specs"),
    ("pascal_curriculum_v3_catalog", "python_curriculum_v3_catalog"),
    ("pascal_v311_builder_mapping", "python_v311_builder_mapping"),
    ("pascal_known_language", "python_known_language"),
    ("seed_pascal_", "seed_python_"),
    ("build_pascal_v311_", "build_python_v311_"),
    ("build_pascal_showcase_", "build_python_showcase_"),
    ("Pascal showcase", "Python showcase"),
    ('LANGUAGE = "pascal"', 'LANGUAGE = "python"'),
    ("starter_pascal", "starter_python"),
    ("reference_solution_pascal", "reference_solution_python"),
    ("reference_code_pascal", "reference_code_python"),
    ("code_examples_pascal", "code_examples_python"),
    ("translation_to_pascal", "translation_to_python"),
    ("translation_snippet_to_pascal", "translation_snippet_to_python"),
    ("translation_python_to_pascal", "translation_to_python"),
    ("block_reorder_pascal", "block_reorder_python"),
    ("pascal_io_program", "python_io_program"),
    ("pascal_debug_starter", "python_debug_starter"),
    ("flowchart_pascal", "flowchart_python"),
    ("mcq_pascal_fragment", "mcq_python_fragment"),
    ("tr_python_to_pascal_code", "tr_pascal_to_python_code"),
    ("tr_cpp_to_pascal_code", "tr_cpp_to_python_code"),
    ("tr_java_to_pascal_code", "tr_java_to_python_code"),
    ("tr_flowchart_to_pascal_code", "tr_flowchart_to_python_code"),
    ("asm_blocks_to_code_pascal", "asm_blocks_to_code_python"),
    ("imp_io_tests_pascal", "imp_io_tests_python"),
    ("imp_text_spec_to_pascal", "imp_text_spec_to_python"),
    ("dbg_pascal_code_fix", "dbg_python_code_fix"),
    ("dbg_pascal_logic_fix", "dbg_python_logic_fix"),
    ("dbg_transfer_syntax_fix", "dbg_transfer_syntax_fix"),
    ('extra.get("curriculum_version") == "3.1.1"', 'extra.get("curriculum_version") == "1.0"'),
    ('curriculum_version: str | int = "2"', 'curriculum_version: str | int = "1.0"'),
    ('curriculum_version=curriculum_version', 'curriculum_version=curriculum_version'),
    ('return "3.1.1"', 'return "1.0"'),
    ("all_pascal_v311_showcase_specs", "all_python_v311_showcase_specs"),
    ("all_pascal_showcase_specs", "all_python_v311_showcase_specs"),
    ("pascal_showcase_all_specs", "python_v311_showcase_all_specs"),
    ("pascal_showcase_core", "python_showcase_core"),
    ("pascal_showcase_next", "python_showcase_next"),
    ("pascal_showcase_student", "python_showcase_student"),
]

OUT_NAMES = {
    "pascal_showcase_core.py": "python_showcase_core.py",
    "pascal_showcase_next.py": "python_showcase_next.py",
    "pascal_showcase_student.py": "python_showcase_student.py",
}


def main() -> int:
    for src in FILES:
        text = (BASE_P / src).read_text(encoding="utf-8")
        for old, new in REPLACEMENTS:
            text = text.replace(old, new)
        text = text.replace(
            "from application.curriculum.python.showcase.python_showcase_registry import",
            "from application.curriculum.pascal.showcase.pascal_showcase_registry import",
        )
        text = text.replace(
            "collection_by_key,\n    effective_title_prefix,\n)",
            "collection_by_key,\n    effective_title_prefix,\n)\n# pascal_showcase_registry kept for legacy v2 compat",
        )
        # student/next: TC bundle from pascal YAML (shared concept ids)
        text = text.replace(
            'CurriculumService(LANGUAGE).get_bundle()',
            'CurriculumService("pascal").get_bundle()',
        )
        dst = BASE_PY / OUT_NAMES[src]
        dst.write_text(text, encoding="utf-8")
        print(f"Wrote {dst}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
