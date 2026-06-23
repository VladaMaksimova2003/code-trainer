#!/usr/bin/env python3
"""Audit chapter 3 loops: metadata, tests vs Python reference."""

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
from loops_ch3_user_payload import (  # noqa: E402
    CH3_TASK_META,
    _KIND_BY_PATTERN,
    build_tasks,
)

CATALOG_GOALS: dict[str, str] = {}
for row in __import__("json").loads((SCRIPTS.parent / "algo_syntax_course.json").read_text(encoding="utf-8")):
    pid = str(row.get("pattern_id") or "")
    if pid.startswith("task_01") or pid.startswith("task_02"):
        num = int(pid.split("_")[1])
        if 17 <= num <= 24:
            CATALOG_GOALS[pid] = str(row.get("goal") or "")


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
        mod = importlib.import_module(f"ch3_user_codes.task_{num:03d}")
        kind = _KIND_BY_PATTERN[pid]
        code = _reference_code(mod, kind)

        meta = ALGO_SYNTAX_META.get(pid) or {}
        user = CH3_TASK_META[pid]

        cat_title = str(meta.get("title") or "")
        if user["title"] != cat_title and cat_title:
            if user["title"].replace("совпадения", "вхождения") != cat_title.replace(
                "совпадения", "вхождения"
            ):
                issues.append(
                    f"[{pid}] Заголовок: payload «{user['title']}» ≠ catalog «{cat_title}»"
                )

        if "обрабатывает последовательность значений" in user.get("goal", ""):
            issues.append(f"[{pid}] Условие в payload — заглушка, не совпадает с catalog goal")

        cat_action = str(meta.get("action") or "")
        if kind == "translation" and cat_action == "assemble":
            issues.append(f"[{pid}] Формат: payload translation ≠ catalog assemble ({cat_action})")
        if kind == "debug" and cat_action == "implement":
            issues.append(f"[{pid}] Формат: payload debug ≠ catalog implement")
        if pid == "task_017" and kind == "translation":
            issues.append(f"[{pid}] Формат: payload перевод, catalog сборка_программы (assemble)")

        cat_tests = meta.get("test_cases") or []
        if cat_tests and cat_tests[0].get("output") == "19" and pid not in {"task_017"}:
            issues.append(f"[{pid}] В ALGO_SYNTAX_META тесты-заглушки (output=19 от другой задачи)")

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

        goal = CATALOG_GOALS.get(pid, "")
        if pid == "task_019" and "yes" in goal.lower() and "prime" in code:
            issues.append(f"[{pid}] Условие: yes/no, код выводит prime/composite")
        if pid == "task_020" and "0" in goal:
            if "for _ in range(n)" in code or "for i := 1 to n" in code:
                if "while" not in code:
                    issues.append(
                        f"[{pid}] Условие: чтение до 0, код читает n чисел (for 1..n)"
                    )
        if pid == "task_021" and "от 1 до n" in goal and "range(1, 11)" in code:
            issues.append(
                f"[{pid}] Условие: таблица 1..n, код всегда умножает на 1..10"
            )
        if pid == "task_024" and "среднее" in goal.lower() and "positives" in code:
            issues.append(
                f"[{pid}] Условие: min max sum avg, код выводит sum min max count_positive"
            )

    print(f"Chapter 3 audit: {len(issues)} issue(s)\n")
    for line in issues:
        print("-", line)


if __name__ == "__main__":
    main()
