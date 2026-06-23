#!/usr/bin/env python3
"""Audit 102 slots + emit flowchart coverage plan data (read-only)."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from application.curriculum.pascal.catalog.pascal_curriculum_v2_catalog import (
    COLLECTION_TARGETS,
    all_pedagogical_slots,
)
from application.curriculum.pascal.showcase.pascal_showcase_core import with_resolved_pattern


def main() -> int:
    rows = []
    for slot in all_pedagogical_slots():
        spec = with_resolved_pattern(slot.to_task_spec())
        rows.append(
            {
                "slot_id": slot.slot_id,
                "collection": slot.collection_key,
                "target_tc": slot.target_tc,
                "action": slot.primary_action,
                "title": slot.title_suffix,
                "builder_key": spec.builder_key,
                "pattern_id": spec.exercise_pattern_id,
                "assignment_type": spec.assignment_type,
            }
        )

    out = BACKEND / "scripts" / "pascal_slots_audit.json"
    out.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(rows)} slots to {out}")
    print("By collection:", dict(Counter(r["collection"] for r in rows)))
    print("By action:", dict(Counter(r["action"] for r in rows)))
    flow = [r for r in rows if "flow" in r["builder_key"] or "flow" in r["pattern_id"]]
    print("Current flowchart slots:", len(flow), [r["slot_id"] for r in flow])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


