"""Patch task_129 meta when shipped in chapter 1 (pas_007)."""

from __future__ import annotations

from typing import Any

_CH1_TASK129_CONCEPTS: dict[str, list[str]] = {
    "pascal": [
        "program_entry",
        "typed_declaration",
        "assignment",
        "stdin_read",
        "stdout_write",
        "pre_condition_loop",
        "arithmetic_ops",
    ],
    "python": [
        "program_entry",
        "assignment",
        "stdin_read",
        "stdout_write",
        "pre_condition_loop",
        "arithmetic_ops",
    ],
    "cpp": [
        "program_entry",
        "import_dependency",
        "typed_declaration",
        "assignment",
        "stdin_read",
        "stdout_write",
        "pre_condition_loop",
        "arithmetic_ops",
    ],
    "csharp": [
        "program_entry",
        "import_dependency",
        "typed_declaration",
        "assignment",
        "stdin_read",
        "stdout_write",
        "pre_condition_loop",
        "arithmetic_ops",
    ],
    "java": [
        "program_entry",
        "import_dependency",
        "typed_declaration",
        "assignment",
        "stdin_read",
        "stdout_write",
        "pre_condition_loop",
        "arithmetic_ops",
    ],
}


def apply_ch1_task129_core_overlay(catalog: dict[str, dict[str, Any]]) -> None:
    row = catalog.get("task_129")
    if not row:
        return
    row["expected_concepts"] = {lang: list(ids) for lang, ids in _CH1_TASK129_CONCEPTS.items()}
    row["chapter_key"] = "algo_basics"
    row["difficulty"] = "easy"
    row["difficulty_ru"] = "легкий"
