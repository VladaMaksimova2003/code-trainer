#!/usr/bin/env python3
"""Audit chapter 5 strings: metadata, tests vs Python reference."""

from __future__ import annotations

import importlib
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
SCRIPTS = BACKEND / "scripts"
for p in (BACKEND, SCRIPTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from application.curriculum.content.algo_syntax_task_extra import ALGO_SYNTAX_META  # noqa: E402
from strings_ch5_user_payload import (  # noqa: E402
    CH5_TASK_META,
    _KIND_BY_PATTERN,
    build_tasks,
)


def _run_python(code: str, stdin: str) -> str:
    buf = io.StringIO()
    ns: dict = {}
    old_in = sys.stdin
    try:
        sys.stdin = io.StringIO(stdin)
        with redirect_stdout(buf):
            exec(compile(code, "<ref>", "exec"), ns, ns)
    finally:
        sys.stdin = old_in
    return buf.getvalue().strip()


def _reference_code(mod, kind: str) -> str:
    if kind == "debug":
        return mod.FIXED_PYTHON
    return mod.PYTHON


def main() -> None:
    issues: list[str] = []

    for task in build_tasks():
        pid = task["pattern_id"]
        num = task["task_num"]
        mod = importlib.import_module(f"ch5_user_codes.task_{num:03d}")
        kind = _KIND_BY_PATTERN[pid]
        code = _reference_code(mod, kind)
        user = CH5_TASK_META[pid]
        meta = ALGO_SYNTAX_META.get(pid) or {}

        cat_title = str(meta.get("title") or "")
        if user["title"] != cat_title and cat_title:
            issues.append(f"[{pid}] Заголовок: payload «{user['title']}» ≠ catalog «{cat_title}»")

        if "анализирует строку" in user.get("goal", ""):
            issues.append(f"[{pid}] Условие в payload — заглушка")

        cat_action = str(meta.get("action") or "")
        kind_map = {"assemble": "assemble", "implement": "translation", "debug": "debug"}
        expected_kind = kind_map.get(cat_action, kind)
        if kind != expected_kind:
            issues.append(
                f"[{pid}] Формат/kind: payload «{kind}» ≠ catalog action «{cat_action}» → ожидался «{expected_kind}»"
            )

        cat_format = str(meta.get("format_ru") or "")
        if cat_format and task.get("task_format") != cat_format:
            issues.append(
                f"[{pid}] format_ru: payload «{task.get('task_format')}» ≠ catalog «{cat_format}»"
            )

        payload_tests = task["tests"]
        cat_tests = meta.get("test_cases") or []
        if cat_tests and payload_tests:
            stale_out = str(cat_tests[0].get("output"))
            expected_out = str(payload_tests[0].get("output"))
            if stale_out != expected_out and stale_out in {"19", "a3b2"}:
                issues.append(
                    f"[{pid}] В ALGO_SYNTAX_META тесты-заглушки (output={stale_out!r})"
                )
            if stale_out != expected_out and stale_out == "yes" and pid not in {
                "task_035",
                "task_038",
            }:
                issues.append(
                    f"[{pid}] В ALGO_SYNTAX_META тесты не совпадают с payload (output={stale_out!r})"
                )

        for idx, tc in enumerate(task["tests"], start=1):
            inp = str(tc.get("inputs") or "")
            expected = str(tc.get("output") or "").strip()
            try:
                actual = _run_python(code, inp)
            except Exception as exc:
                issues.append(f"[{pid}] тест #{idx}: Python reference упал: {exc}")
                continue
            if actual != expected:
                issues.append(
                    f"[{pid}] тест #{idx}: ожидалось {expected!r}, код дал {actual!r}"
                )

        goal = str(user.get("goal") or "")
        gl = goal.lower()
        if pid == "task_033" and "количество символов" in gl and "ch = input" in code:
            issues.append(f"[{pid}] Условие: длина строки, код — подсчёт вхождений символа")
        if pid == "task_040" and "гласн" in gl:
            if "palindrome" in code.lower() or ("yes" in code and "vowel" not in code.lower()):
                if "aeiou" not in code and "'aeiou'" not in code:
                    issues.append(
                        f"[{pid}] Условие: гласные буквы, код не считает гласные"
                    )

    print(f"Chapter 5 audit: {len(issues)} issue(s)\n")
    for line in issues:
        print("-", line)


if __name__ == "__main__":
    main()
