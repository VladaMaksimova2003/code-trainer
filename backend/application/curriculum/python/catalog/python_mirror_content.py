"""Pull Python task content from mirrored Pascal v3.1.1 slots."""

from __future__ import annotations

from application.curriculum.mirror.curriculum_slot_mirror import neutralize_title
from application.curriculum.mirror.curriculum_slot_mirror_map import (
    is_python_only_slot,
    python_to_pascal_slot,
)

# Python debug starters keyed by python slot (mirrors Pascal bug pedagogy).
_PYTHON_DEBUG_FROM_MIRROR: dict[str, str] = {
    "pyk_02": "if True:\nprint('ok')",
    "pyt_02": "x == 1\nprint(x)",
    "pyt_10": "x = 7.9\nn = x\nm = round(x)",
    "pye_01": "result = 5 / 2\nprint(result)",
    "pyi_01": "name = input\nprint(name)",
    "pyi_04": "s = input()\nn = s\nprint(n)",
    "pya_03": "items = [10, 20, 30]\nprint(items[1])",
    "pya_04": "items = [10, 20, 30]\nfor i in range(1, len(items)):\n    print(items[i])",
    "pyl_07": "for i in range(1, n):\n    print(i)",
    "pyl_14": "for i in range(5):\n    i = 10\n    print(i)",
    "pyf_03": "def double(n):\n    n * 2",
    "pys_03": "s = 'abc'\nprint(s[len(s)])",
    "pyo_09": "class Demo:\n    def show():\n        print('hi')",
}


def mirrored_pascal_slot(python_slot_id: str) -> str | None:
    if is_python_only_slot(python_slot_id):
        return None
    return python_to_pascal_slot(python_slot_id)


def python_reference_from_mirror(python_slot_id: str) -> str | None:
    pas_id = mirrored_pascal_slot(python_slot_id)
    if not pas_id:
        return None
    from application.curriculum.pascal.catalog.pascal_v311_known_code import get_known_code

    known = get_known_code(pas_id)
    if known and str(known[0] or "").strip():
        return str(known[0]).strip()
    try:
        from application.curriculum.pascal.catalog import pascal_v311_content as pc

        ref = pc._reference_solution(pas_id, "")
        if ref and ref.strip() and ref.strip() != pc._PASCAL_SNIPPET:
            # Pascal reference — only use if it looks like Python (heuristic).
            if "program " not in ref.lower() and "begin" not in ref.lower():
                return ref.strip()
    except Exception:
        pass
    return None


def python_debug_starter_from_mirror(python_slot_id: str) -> str | None:
    if python_slot_id in _PYTHON_DEBUG_FROM_MIRROR:
        return _PYTHON_DEBUG_FROM_MIRROR[python_slot_id]
    pas_id = mirrored_pascal_slot(python_slot_id)
    if not pas_id:
        return None
    ref = python_reference_from_mirror(python_slot_id)
    if not ref:
        return None
    # Generic: reference with a plausible bug for debug tasks without explicit starter.
    if "==" in ref and ":=" not in ref:
        return ref.replace("=", "==", 1)
    return None


def python_test_cases_from_mirror(python_slot_id: str) -> list[dict[str, str]] | None:
    pas_id = mirrored_pascal_slot(python_slot_id)
    if not pas_id:
        return None
    try:
        from application.curriculum.pascal.catalog import pascal_v311_content as pc

        cases = pc._SLOT_TEST_CASES.get(pas_id)
        if cases:
            return [dict(c) for c in cases]
    except Exception:
        pass
    return None


def neutral_title_for_mirror(python_slot_id: str, fallback: str) -> str:
    pas_id = mirrored_pascal_slot(python_slot_id)
    if pas_id:
        from application.curriculum.mirror.curriculum_slot_mirror import canonical_title_for_slot

        canonical = canonical_title_for_slot(pas_id)
        if canonical:
            return canonical
        try:
            from application.curriculum.pascal.catalog.pascal_curriculum_v3_catalog import (
                all_v311_task_records as pas_records,
            )

            for rec in pas_records():
                if rec.slot_id == pas_id:
                    return neutralize_title(rec.title)
        except Exception:
            pass
    return neutralize_title(fallback)


def neutral_goal_from_mirror(python_slot_id: str, fallback: str) -> str:
    pas_id = mirrored_pascal_slot(python_slot_id)
    if not pas_id:
        return neutralize_title(fallback)
    try:
        from application.curriculum.pascal.catalog.pascal_curriculum_v3_catalog import (
            all_v311_task_records as pas_records,
        )

        for rec in pas_records():
            if rec.slot_id == pas_id:
                goal = str(rec.educational_goal or fallback)
                for old, new in (
                    ("Pascal", ""),
                    ("Python", ""),
                    ("Readln", "ввод"),
                    ("Writeln", "вывод"),
                    ("program/begin/end", "структура программы"),
                    ("Result", "return"),
                    ("procedure", "функция"),
                ):
                    goal = goal.replace(old, new)
                return " ".join(goal.split())
    except Exception:
        pass
    return neutralize_title(fallback)
