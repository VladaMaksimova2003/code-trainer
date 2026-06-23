"""Resolve executable test cases for Python Course v1 catalog tasks."""

from __future__ import annotations

import re
from typing import Any

TaskRow = tuple[str, str, str, str, str, str, str, str, str, str]

_PYTHON_PROGRAM = (
    "def main():\n"
    "    x = 1\n"
    "    y = x + 1\n"
    "    print(y)\n\n"
    "if __name__ == '__main__':\n"
    "    main()\n"
)

_PYTHON_SNIPPET = "x = 1\ny = x + 1\nprint(y)"

_NON_EXECUTABLE_FORMATS = frozenset(
    {
        "выбор_фрагмента",
        "блок-схема_по_коду",
        "поиск_ошибки",
    }
)

_PROBE = "ok"


def wrap_python_snippet(snippet: str) -> str:
    body = str(snippet or "").strip()
    if not body:
        return ""
    if "if __name__" in body:
        return body
    lines = [line.rstrip() for line in body.splitlines() if line.strip()]
    indented = "\n".join(f"    {line}" for line in lines)
    return (
        "def _run():\n"
        f"{indented}\n"
        f"    print('{_PROBE}')\n\n"
        "if __name__ == '__main__':\n"
        "    _run()\n"
    )


def _reference_solution(slot_id: str, _features: str) -> str:
    from application.curriculum.python.catalog.python_v311_content import reference_solution_for_slot

    return reference_solution_for_slot(slot_id)


def _debug_solution(slot_id: str) -> str:
    return _reference_solution(slot_id, "")


def derive_test_cases(row: TaskRow, extra: dict[str, Any] | None = None) -> list[dict[str, str]]:
    slot_id, _chapter, _title, task_format, _action, _pattern, _goal, features, _diff, _legacy = row
    extra = extra or {}

    if task_format in _NON_EXECUTABLE_FORMATS:
        return [{"inputs": "", "output": _PROBE}]

    if extra.get("test_cases"):
        return [dict(c) for c in extra["test_cases"]]

    if task_format in {"исправление", "поиск_ошибки"}:
        return [{"inputs": "", "output": _PROBE}]

    ref = str(extra.get("reference_solution_python") or _reference_solution(slot_id, features))
    if task_format == "перевод_фрагмента":
        ref = wrap_python_snippet(ref)
    elif task_format == "перевод_программы" and "def " in ref and "if __name__" not in ref:
        ref = wrap_python_snippet(ref)

    if not ref.strip():
        return [{"inputs": "", "output": _PROBE}]

    try:
        from application.curriculum.python.catalog.python_v311_measured_outputs import MEASURED_OUTPUTS

        measured = MEASURED_OUTPUTS.get(slot_id)
        if measured:
            return [dict(c) for c in measured]
    except ImportError:
        pass

    # Static fallback — enough for catalog validation; runtime seed may refine.
    if re.search(r"input\s*\(", ref):
        return [{"inputs": "1\n", "output": _PROBE}]
    if re.search(r"print\s*\(", ref):
        return [{"inputs": "", "output": _PROBE}]
    return [{"inputs": "", "output": _PROBE}]
