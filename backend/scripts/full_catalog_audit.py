"""Read-only audit: full MPLT catalog vs DB."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import psycopg2

SCRIPTS = Path(__file__).resolve().parent
BACKEND = SCRIPTS.parent
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(SCRIPTS))

from algo_v128_catalog import ALGO_SYNTAX_META, V128_CORE_TASK_COUNT, _TASK_INDEX  # noqa: E402
from algo_v192_plan import V192_EXPANSION_INDEX, V192_TARGET_TASK_COUNT  # noqa: E402
from application.tasks.services.teacher_assembly_preservation import has_teacher_assembly_override  # noqa: E402
from application.tasks.services.block_reorder_helpers import is_build_from_blocks_task_type  # noqa: E402
from v128_test_matrix import is_placeholder_test, PLACEHOLDER_SCAFFOLD_PATTERNS  # noqa: E402

DB = dict(host="localhost", port=5433, dbname="code_trainer", user="code_trainer", password="change_me")

V128_PATTERN_IDS = {f"task_{n:03d}" for n in range(1, V128_CORE_TASK_COUNT + 1)}
V192_PATTERN_IDS = {f"task_{n:03d}" for n in range(1, V192_TARGET_TASK_COUNT + 1)}
CATALOG_BY_PATTERN = {r["pattern_id"]: r for r in _TASK_INDEX}
for row in V192_EXPANSION_INDEX:
    CATALOG_BY_PATTERN.setdefault(row["pattern_id"], row)


def pattern_num(pid: str | None) -> int | None:
    if not pid:
        return None
    m = re.match(r"task_(\d+)$", str(pid))
    return int(m.group(1)) if m else None


def parse_json(val: Any) -> Any:
    if isinstance(val, str):
        return json.loads(val)
    return val


def primary_action(row: dict[str, Any]) -> str:
    ce = row.get("code_examples") or {}
    showcase = ce.get("curriculum_showcase") or {}
    action = (
        showcase.get("primary_action")
        or showcase.get("action")
        or ce.get("action")
        or ""
    )
    if not action:
        pid = row.get("slot_pattern_id")
        cat = CATALOG_BY_PATTERN.get(str(pid or ""), {})
        action = cat.get("action") or ""
    action = str(action).strip().lower()
    if action == "implement":
        return "translate"
    return action


def has_buggy_split(ce: dict) -> bool:
    if not isinstance(ce, dict):
        return False
    py_buggy = str(ce.get("buggy_python") or "").strip()
    py_fixed = str(ce.get("python") or "").strip()
    pas_buggy = str(ce.get("buggy_pascal") or "").strip()
    pas_fixed = str(ce.get("pascal") or "").strip()
    if py_buggy and py_fixed and py_buggy != py_fixed:
        return True
    if pas_buggy and pas_fixed and pas_buggy != pas_fixed:
        return True
    impls = ce.get("implementations") or {}
    for lang in ("python", "pascal"):
        impl = impls.get(lang) or {}
        buggy = str(impl.get("buggy_code") or "").strip()
        fixed = str(impl.get("fixed_code") or impl.get("reference_code") or "").strip()
        if buggy and fixed and buggy != fixed:
            return True
    return False


def has_hints(ce: dict, showcase: dict) -> bool:
    hints = ce.get("hints") or showcase.get("hints") or []
    return bool(hints)


def has_post_solve(ce: dict, showcase: dict) -> bool:
    return bool(
        ce.get("post_solve_explanation")
        or showcase.get("post_solve_explanation")
    )


def tests_are_all_placeholders(tests: list) -> bool:
    if not tests:
        return False
    return all(is_placeholder_test(t) for t in tests)


def is_reorder_blocks_task_type(raw: str) -> bool:
    v = str(raw or "").strip().lower()
    return v in {"block_reorder", "task_reorder_blocks"}


def load_db_tasks(cur) -> list[dict[str, Any]]:
    cur.execute(
        """
        select id, title, task_type, test_cases, code_examples,
               exists(select 1 from block_reorder_task br where br.task_id = task.id) as has_br
        from task
        order by id
        """
    )
    rows: list[dict[str, Any]] = []
    for did, title, task_type, tests, ce, has_br in cur.fetchall():
        tests = parse_json(tests) or []
        ce = parse_json(ce) or {}
        showcase = ce.get("curriculum_showcase") or {}
        slot_pattern_id = (
            showcase.get("slot_pattern_id")
            or ce.get("slot_pattern_id")
            or None
        )
        rows.append(
            {
                "id": did,
                "title": title,
                "task_type": str(task_type or ""),
                "has_block_reorder_row": bool(has_br),
                "test_cases": tests if isinstance(tests, list) else [],
                "code_examples": ce if isinstance(ce, dict) else {},
                "curriculum_showcase": showcase if isinstance(showcase, dict) else {},
                "slot_pattern_id": str(slot_pattern_id) if slot_pattern_id else None,
            }
        )
    return rows


def audit() -> dict[str, Any]:
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    tasks = load_db_tasks(cur)
    cur.close()
    conn.close()

    total_db = len(tasks)
    catalog_tasks = [t for t in tasks if t.get("slot_pattern_id")]
    catalog_by_pid = {t["slot_pattern_id"]: t for t in catalog_tasks}

    def count_action(action: str) -> int:
        return sum(1 for t in catalog_tasks if primary_action(t) == action)

    build_from_blocks = sum(
        1 for t in tasks if is_build_from_blocks_task_type(t["task_type"])
    )
    reorder_blocks = sum(
        1 for t in tasks
        if is_reorder_blocks_task_type(t["task_type"])
        or (t["has_block_reorder_row"] and not is_build_from_blocks_task_type(t["task_type"]))
    )
    # Also count explicit assignment string if present in DB
    reorder_blocks_alt = sum(
        1 for t in tasks if str(t["task_type"]).lower() == "task_reorder_blocks"
    )

    teacher_override = sum(
        1 for t in tasks if has_teacher_assembly_override(t["code_examples"])
    )
    buggy_split = sum(1 for t in tasks if has_buggy_split(t["code_examples"]))
    hints_n = sum(
        1 for t in tasks if has_hints(t["code_examples"], t["curriculum_showcase"])
    )
    post_solve_n = sum(
        1 for t in tasks if has_post_solve(t["code_examples"], t["curriculum_showcase"])
    )

    placeholders_only_tests = sum(
        1 for t in tasks if tests_are_all_placeholders(t["test_cases"])
    )
    scaffold_placeholder_slots = sum(
        1 for t in catalog_tasks
        if t.get("slot_pattern_id") in PLACEHOLDER_SCAFFOLD_PATTERNS
    )
    tasks_with_any_placeholder_test = sum(
        1 for t in tasks
        if any(is_placeholder_test(x) for x in t["test_cases"])
    )

    v128_in_db = [
        t for t in catalog_tasks
        if (n := pattern_num(t["slot_pattern_id"])) is not None and n <= V128_CORE_TASK_COUNT
    ]
    v192_in_db = [
        t for t in catalog_tasks
        if (n := pattern_num(t["slot_pattern_id"])) is not None and n <= V192_TARGET_TASK_COUNT
    ]

    v128_patterns_present = {
        t["slot_pattern_id"] for t in v128_in_db if t.get("slot_pattern_id")
    }
    v192_patterns_present = {
        t["slot_pattern_id"] for t in v192_in_db if t.get("slot_pattern_id")
    }

    task_type_breakdown = {}
    for t in tasks:
        tt = t["task_type"] or "(empty)"
        task_type_breakdown[tt] = task_type_breakdown.get(tt, 0) + 1

    action_breakdown = {}
    for t in catalog_tasks:
        act = primary_action(t) or "(unknown)"
        action_breakdown[act] = action_breakdown.get(act, 0) + 1

    return {
        "1_total_tasks_in_db": total_db,
        "2_debug": count_action("debug"),
        "3_assemble": count_action("assemble"),
        "4_translate": count_action("translate"),
        "5_placeholders_scaffold_slots": scaffold_placeholder_slots,
        "5_placeholders_only_tests": placeholders_only_tests,
        "5_tasks_with_any_placeholder_test": tasks_with_any_placeholder_test,
        "5_scaffold_expected_in_catalog": len(PLACEHOLDER_SCAFFOLD_PATTERNS),
        "6_task_build_from_blocks": build_from_blocks,
        "7_task_reorder_blocks": reorder_blocks_alt,
        "7_block_reorder_task_rows": sum(1 for t in tasks if t["has_block_reorder_row"]),
        "7_task_reorder_blocks_detail": {
            "task_type_task_reorder_blocks": reorder_blocks_alt,
            "task_type_block_reorder": sum(
                1 for t in tasks if str(t["task_type"]).lower() == "block_reorder"
            ),
            "has_block_reorder_row_not_build": sum(
                1 for t in tasks
                if t["has_block_reorder_row"] and not is_build_from_blocks_task_type(t["task_type"])
            ),
        },
        "8_teacher_override": teacher_override,
        "9_fixed_buggy_split": buggy_split,
        "10_hints": hints_n,
        "11_post_solve": post_solve_n,
        "12_v128_catalog_tasks_in_db": len(v128_in_db),
        "12_v128_unique_patterns_in_db": len(v128_patterns_present),
        "12_v128_expected": V128_CORE_TASK_COUNT,
        "13_v192_catalog_tasks_in_db": len(v192_in_db),
        "13_v192_unique_patterns_in_db": len(v192_patterns_present),
        "13_v192_expected": V192_TARGET_TASK_COUNT,
        "catalog_tasks_with_slot_pattern_id": len(catalog_tasks),
        "catalog_unique_patterns": len(catalog_by_pid),
        "task_type_breakdown": dict(sorted(task_type_breakdown.items(), key=lambda x: -x[1])),
        "catalog_action_breakdown": dict(sorted(action_breakdown.items(), key=lambda x: -x[1])),
        "non_catalog_db_tasks": total_db - len(catalog_tasks),
        "missing_v128_patterns": sorted(V128_PATTERN_IDS - v128_patterns_present),
        "missing_v192_patterns": sorted(V192_PATTERN_IDS - v192_patterns_present),
    }


def main() -> None:
    result = audit()
    out = BACKEND.parent / "docs" / "full_catalog_audit_report.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
