#!/usr/bin/env python3
"""Validate chapter-1 algo_basics task payload consistency."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(BACKEND / "scripts"))

from algo_basics_ch1_user_payload import TASKS, CHAPTER_KEY
from algo_v128_catalog import _TASK_INDEX
from application.curriculum.display.chapter1_algo_basics_hints import CHAPTER1_HINTS
from application.curriculum.content.ch1_fragment_assembly import gap_count_for_template
from application.curriculum.content.v4_assembly_builder import assembly_payload_for_format
from application.curriculum.validation.expected_concept_checker import detect_expected_concepts_multilang

_LANGS = ("pascal", "python", "cpp", "csharp", "java")


def _run_python_case(code: str, stdin: str, expected: str) -> str | None:
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as handle:
        handle.write(code)
        path = handle.name
    try:
        proc = subprocess.run(
            [sys.executable, path],
            input=stdin,
            text=True,
            capture_output=True,
            timeout=8,
            check=False,
        )
        if proc.returncode != 0:
            return f"exit {proc.returncode}: {(proc.stderr or proc.stdout)[:180]}"
        actual = (proc.stdout or "").strip()
        if actual != expected.strip():
            return f"expected {expected!r}, got {actual!r}"
        return None
    finally:
        Path(path).unlink(missing_ok=True)


def main() -> int:
    errors: list[str] = []
    catalog_rows = {
        str(r["pattern_id"]): r
        for r in _TASK_INDEX
        if r.get("chapter_key") == CHAPTER_KEY
    }
    if len(catalog_rows) != 8:
        errors.append(f"expected 8 catalog rows for {CHAPTER_KEY}, got {len(catalog_rows)}")
    if len(TASKS) != 8:
        errors.append(f"expected 8 TASKS, got {len(TASKS)}")

    for task in TASKS:
        num = int(task["task_num"])
        pid = str(task["pattern_id"])
        row = catalog_rows.get(pid)
        if row is None:
            errors.append(f"task {num}: pattern {pid} missing from catalog")
            continue
        if int(row["task_num"]) != num:
            errors.append(f"task {num}: catalog task_num mismatch {row['task_num']}")
        if not task.get("title"):
            errors.append(f"task {num}: missing title")
        if not task.get("detailed_description"):
            errors.append(f"task {num}: missing description")
        hints = task.get("hints") or []
        if not hints:
            errors.append(f"task {num}: no hints")
        elif pid not in CHAPTER1_HINTS:
            errors.append(f"task {num}: hints not in CHAPTER1_HINTS")
        tests = task.get("tests") or []
        if len(tests) < 3:
            errors.append(f"task {num}: expected >=3 test cases, got {len(tests)}")
        for case in tests:
            if not str(case.get("inputs", "")).strip():
                errors.append(f"task {num}: empty test input")
            if case.get("output") is None:
                errors.append(f"task {num}: missing test output")

        catalog_format = str(row.get("format_ru") or "")
        if str(task.get("task_format") or "") != catalog_format:
            errors.append(
                f"task {num}: task_format {task.get('task_format')!r} != catalog {catalog_format!r}",
            )

        kind = str(task.get("kind") or "")
        if kind == "debug":
            fixed = task.get("fixed") or {}
            buggy = task.get("buggy") or {}
            for lang in _LANGS:
                if not str(fixed.get(lang, "")).strip():
                    errors.append(f"task {num} debug: missing fixed {lang}")
                if not str(buggy.get(lang, "")).strip():
                    errors.append(f"task {num} debug: missing buggy {lang}")
            samples = [(lang, fixed[lang]) for lang in _LANGS if fixed.get(lang)]
        else:
            codes = task.get("codes") or {}
            for lang in _LANGS:
                if not str(codes.get(lang, "")).strip():
                    errors.append(f"task {num}: missing code {lang}")
            samples = [(lang, codes[lang]) for lang in _LANGS if codes.get(lang)]

            if catalog_format == "сборка_фрагмента":
                for lang in _LANGS:
                    code = str(codes.get(lang) or "")
                    if not code.strip():
                        continue
                    _orig, template, blocks, order = assembly_payload_for_format(
                        catalog_format,
                        lang,
                        code,
                        pattern_id=pid,
                    )
                    gaps = gap_count_for_template(template)
                    if gaps < 3:
                        errors.append(f"task {num} {lang}: fragment has {gaps} gaps, need >=3")
                    if len(order) != gaps:
                        errors.append(
                            f"task {num} {lang}: correct_order len {len(order)} != gaps {gaps}",
                        )
                    if not blocks:
                        errors.append(f"task {num} {lang}: empty assembly blocks")

        expected = detect_expected_concepts_multilang(samples)
        if not expected:
            errors.append(f"task {num}: no expected concepts detected")
        catalog_features = set(str(row.get("features") or "").split(";"))
        for lang, ids in expected.items():
            if not ids:
                errors.append(f"task {num}: empty expected concepts for {lang}")

        if kind == "debug":
            py_code = str((task.get("fixed") or {}).get("python") or "")
        else:
            py_code = str((task.get("codes") or {}).get("python") or "")
        if py_code.strip():
            for index, case in enumerate(tests):
                err = _run_python_case(py_code, str(case.get("inputs") or ""), str(case.get("output") or ""))
                if err:
                    errors.append(f"task {num} python test {index + 1}: {err}")

    if errors:
        print("CH1 VALIDATION FAILED:")
        for err in errors:
            print(" -", err)
        return 1
    print("CH1 validation OK:", len(TASKS), "tasks")
    for task in TASKS:
        print(
            f"  {task['task_num']:02d} {task['pattern_id']}: "
            f"{task['title'][:45]} | tests={len(task['tests'])} hints={len(task['hints'])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
