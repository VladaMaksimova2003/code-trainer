"""Generate debug-import roadmap for remaining 35 slots."""
from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
sys.path.insert(0, str(SCRIPTS.parent))

import psycopg2
from algo_v128_catalog import V128_CHAPTER_TITLES, _TASK_INDEX
from algo_v192_plan import V192_EXPANSION_INDEX
from debug_course_audit import (
    APPLIED_IMPORT_IDS,
    DB,
    audit_row,
    load_import_overrides,
)

APPLIED = {
    "task_004", "task_007", "task_023", "task_028", "task_031", "task_036", "task_039",
    "task_044", "task_047", "task_052", "task_055", "task_060", "task_092",
}
APPLIED_IMPORT_IDS.update(load_import_overrides())

ALL_DEBUG_CATALOG = [
    r for r in list(_TASK_INDEX) + list(V192_EXPANSION_INDEX)
    if r.get("action") == "debug"
]


def chapter_title(key: str) -> str:
    return V128_CHAPTER_TITLES.get(key, key)


def pattern_num(pid: str) -> int:
    return int(pid.split("_")[1])


def is_expansion(pid: str) -> bool:
    return pattern_num(pid) > 128


def fixed_ratio(s: str) -> float:
    if "/" not in s:
        return 0.0
    ok, total = s.split("/", 1)
    try:
        return int(ok) / int(total) if int(total) else 0.0
    except ValueError:
        return 0.0


def bucket(row: dict) -> str:
    pid = row["task_id"]
    if row["status"] == "applied":
        return "applied"
    fixed = row["fixed_validation"]
    ratio = fixed_ratio(fixed)
    conflicts = row.get("conflicts") or []
    exp = is_expansion(pid)

    if row["status"] == "unresolved":
        return "C"

    if ratio >= 0.8 and len(conflicts) <= 1 and not exp:
        if pid in {"task_012", "task_020"}:
            return "A"
        return "B" if ratio < 1.0 else "A"

    if exp and ratio == 0.0:
        return "D"

    if exp:
        return "D" if ratio < 0.5 else "B"

    if ratio >= 0.8:
        return "B"

    if pid in {"task_068", "task_076"} and ratio == 0.0:
        return "B"  # simple algorithms, likely wrong code pasted

    if pid in {"task_084", "task_087", "task_095", "task_100", "task_103", "task_108", "task_111", "task_124", "task_127"}:
        if ratio == 0.0:
            return "D" if exp else ("B" if pid in {"task_068", "task_076"} else "D")

    return "D"


def needs_x5(row: dict) -> str:
    if row.get("has_buggy_split"):
        return "partial (update)"
    tt = row.get("task_type", "")
    if "translate" in tt:
        return "yes (translate debug)"
    return "yes"


def effort(row: dict, b: str) -> str:
    pid = row["task_id"]
    ratio = fixed_ratio(row["fixed_validation"])
    exp = is_expansion(pid)
    ch = row.get("chapter_key", "")

    if b == "A":
        return "low"
    if b == "C":
        return "high" if row["status"] == "unresolved" and len(row.get("conflicts") or []) >= 3 else "medium"
    if b == "B":
        if ratio >= 0.8:
            return "low" if pid in {"task_012", "task_020", "task_063"} else "medium"
        if ch in {"aggregation", "maps", "search_sort"}:
            return "medium"
        return "medium"
    # D defer
    if ch in {"files_modules", "linked_lists", "trees_graphs", "oop", "inheritance_capstone"}:
        return "high"
    if exp:
        return "medium"
    return "high"


def problem_reason(row: dict) -> str:
    parts: list[str] = []
    if not row.get("has_buggy_split"):
        parts.append("нет fixed/buggy split")
    if row.get("hints", 0) == 0 or not row.get("post_solve"):
        parts.append("нет hints/post_solve")
    fixed = row["fixed_validation"]
    if fixed != "n/a" and not fixed.startswith(f"{fixed.split('/')[1]}/") if "/" in fixed else True:
        ok, total = (fixed.split("/") + ["0"])[:2]
        if ok != total:
            parts.append(f"fixed проходит {fixed}")
    if row.get("conflicts"):
        parts.append("конфликт: " + ", ".join(row["conflicts"]))
    if is_expansion(row["task_id"]):
        parts.append("v192 expansion slot")
    return "; ".join(parts) if parts else "legacy scaffold"


def recommend(row: dict, b: str) -> str:
    pid = row["task_id"]
    if b == "A":
        return "Batch 4 кандидат: починить 1 тест + import override"
    if b == "B":
        if pid in {"task_012", "task_020"}:
            return "Следующий import после утверждения canon (1 failing test)"
        if pid == "task_063":
            return "Уточнить sort order в canon, затем import"
        if pid in {"task_068", "task_076"}:
            return "Заменить чужой код на canon алгоритма + buggy"
        return "Import после короткой conflict-card"
    if b == "C":
        return "Conflict-card → утверждение canon → только потом import"
    return "Отложить до v128 core закрыт; для диплома достаточно 13/32 v128 applied"


def main() -> None:
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    rows = []
    for cat in sorted(ALL_DEBUG_CATALOG, key=lambda r: r.get("task_num", pattern_num(r["pattern_id"]))):
        r = audit_row(cur, cat["pattern_id"], cat)
        r["chapter_key"] = cat.get("chapter_key", "")
        r["chapter"] = chapter_title(str(cat.get("chapter_key", "")))
        r["task_num"] = cat.get("task_num", pattern_num(cat["pattern_id"]))
        r["difficulty"] = cat.get("difficulty", "")
        r["expansion"] = is_expansion(cat["pattern_id"])
        cur.execute(
            "select task_type from task where code_examples->'curriculum_showcase'->>'slot_pattern_id'=%s",
            (cat["pattern_id"],),
        )
        tt = cur.fetchone()
        r["task_type"] = tt[0] if tt else ""
        b = bucket(r)
        r["roadmap_bucket"] = b
        r["effort"] = effort(r, b)
        r["needs_x5"] = needs_x5(r)
        r["problem"] = problem_reason(r)
        r["recommendation"] = recommend(r, b)
        rows.append(r)
    cur.close()
    conn.close()

    remaining = [r for r in rows if r["task_id"] not in APPLIED]
    summary = {
        "total_debug": len(rows),
        "applied": len(APPLIED),
        "remaining": len(remaining),
        "v128_debug": sum(1 for r in rows if not r["expansion"]),
        "v192_debug": sum(1 for r in rows if r["expansion"]),
        "buckets_remaining": {
            b: [x["task_id"] for x in remaining if x["roadmap_bucket"] == b]
            for b in ("A", "B", "C", "D")
        },
        "by_status_remaining": {},
        "rows": rows,
    }
    for st in ("damaged", "unresolved", "legacy"):
        summary["by_status_remaining"][st] = [
            r["task_id"] for r in remaining
            if (r["status"] in ("damaged", "unresolved") and r["status"] == st)
            or (st == "legacy" and r["status"] not in ("applied", "damaged", "unresolved"))
        ]

    out = SCRIPTS.parent.parent / "docs" / "debug_import_roadmap.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, ensure_ascii=False, indent=2))
    print("--- remaining sample ---")
    for r in remaining[:5]:
        print(r["task_id"], r["roadmap_bucket"], r["effort"], r["fixed_validation"])


if __name__ == "__main__":
    main()
