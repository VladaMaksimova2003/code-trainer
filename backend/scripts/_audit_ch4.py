#!/usr/bin/env python3
"""Audit chapter 4 arrays: metadata, tests vs Python reference."""

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
from arrays_ch4_user_payload import (  # noqa: E402
    CH4_TASK_META,
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
        mod = importlib.import_module(f"ch4_user_codes.task_{num:03d}")
        kind = _KIND_BY_PATTERN[pid]
        code = _reference_code(mod, kind)
        user = CH4_TASK_META[pid]
        meta = ALGO_SYNTAX_META.get(pid) or {}

        cat_title = str(meta.get("title") or "")
        if user["title"] != cat_title and cat_title:
            issues.append(f"[{pid}] Заголовок: payload «{user['title']}» ≠ catalog «{cat_title}»")

        if "работает с набором чисел" in user.get("goal", ""):
            issues.append(f"[{pid}] Условие в payload — заглушка")

        cat_action = str(meta.get("action") or "")
        kind_map = {"assemble": "assemble", "implement": "translation", "debug": "debug"}
        expected_kind = kind_map.get(cat_action, kind)
        if kind != expected_kind:
            issues.append(
                f"[{pid}] Формат/kind: payload «{kind}» ≠ catalog action «{cat_action}» → ожидался «{expected_kind}»"
            )

        cat_tests = meta.get("test_cases") or []
        if cat_tests and str(cat_tests[0].get("output")) == "19":
            issues.append(f"[{pid}] В ALGO_SYNTAX_META тесты-заглушки (output=19)")

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
                    f"[{pid}] тест #{idx}: ожидалось {expected!r}, код дал {actual!r} | stdin={inp[:40]!r}..."
                )

        goal = str(user.get("goal") or "")
        if pid == "task_026" and "k" in goal.lower() and "k" not in code.split("\n")[0]:
            if "k" not in code and "readln(k" not in code:
                issues.append(f"[{pid}] Условие: сдвиг на k, код сдвигает только на 1")
        if pid == "task_031":
            if "отсортирован" in goal.lower() and "n, m" in code and "max" in code.lower():
                issues.append(
                    f"[{pid}] Условие: слияние двух отсортированных массивов, код — максимум в матрице n×m"
                )
        if pid == "task_030" and "yes" in goal.lower() and "prime" in code:
            issues.append(f"[{pid}] Код выводит prime вместо yes/no")

    print(f"Chapter 4 audit: {len(issues)} issue(s)\n")
    for line in issues:
        print("-", line)


if __name__ == "__main__":
    main()
