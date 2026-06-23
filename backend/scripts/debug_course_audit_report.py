"""Emit UTF-8 JSON report from debug_course_audit."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import psycopg2
from debug_course_audit import (
    APPLIED_IMPORT_IDS,
    CATALOG_DEBUG,
    DB,
    audit_row,
    load_import_overrides,
)

APPLIED_IMPORT_IDS.update(load_import_overrides() & {r["pattern_id"] for r in CATALOG_DEBUG})

conn = psycopg2.connect(**DB)
cur = conn.cursor()
rows = [audit_row(cur, r["pattern_id"], r) for r in sorted(CATALOG_DEBUG, key=lambda x: x["task_num"])]
cur.close()
conn.close()

summary = {
    "total": len(rows),
    "by_status": {st: sum(1 for r in rows if r.get("status") == st) for st in ("applied", "clean", "damaged", "unresolved")},
    "rows": rows,
    "remaining_damaged": [r["task_id"] for r in rows if r["status"] == "damaged"],
    "remaining_unresolved": [r["task_id"] for r in rows if r["status"] == "unresolved"],
    "without_buggy_split": [r["task_id"] for r in rows if not r.get("has_buggy_split")],
    "without_hints_post_solve": [r["task_id"] for r in rows if r.get("hints", 0) == 0 or not r.get("post_solve")],
    "with_conflicts": [{"task_id": r["task_id"], "conflicts": r.get("conflicts") or []} for r in rows if r.get("conflicts")],
}

out = Path(__file__).resolve().parent.parent.parent / "docs" / "debug_course_audit_report.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(str(out))
