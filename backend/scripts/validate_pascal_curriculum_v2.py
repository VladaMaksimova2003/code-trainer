#!/usr/bin/env python3
"""Validate Pascal curriculum v2 pedagogical slots against YAML curriculum."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict

from application.curriculum.pascal.catalog.pascal_curriculum_v2_catalog import (
    COLLECTION_TARGETS,
    all_pedagogical_slots,
    slots_by_collection,
)
from application.curriculum.pascal.showcase.pascal_showcase_core import with_resolved_pattern
from application.curriculum.task_curriculum_link_service import validate_task_curriculum_link_metadata


def main() -> int:
    slots = all_pedagogical_slots()
    errors: list[str] = []

    if len(slots) != 102:
        errors.append(f"Expected 102 slots, got {len(slots)}")

    grouped = slots_by_collection()
    for key, target in COLLECTION_TARGETS.items():
        actual = len(grouped.get(key, ()))
        if actual != target:
            errors.append(f"Collection {key}: expected {target}, got {actual}")

    implement_by_tc: Counter[str] = Counter()
    analyze_tcs: set[str] = set()
    recognize_primary = 0

    for slot in slots:
        if slot.primary_action == "recognize":
            recognize_primary += 1
            errors.append(f"{slot.slot_id}: recognize as primary_action")
        if "recognize" in slot.secondary_actions:
            pass
        if slot.primary_action == "implement":
            implement_by_tc[slot.target_tc] += 1
        if slot.primary_action == "analyze":
            analyze_tcs.add(slot.target_tc)

        task_spec = with_resolved_pattern(slot.to_task_spec())
        try:
            meta = validate_task_curriculum_link_metadata(
                "pascal",
                task_spec.technical_concept_id,
                task_spec.exercise_pattern_id,
            )
            if meta["action"] != slot.primary_action:
                errors.append(
                    f"{slot.slot_id}: pattern action {meta['action']} != primary {slot.primary_action}"
                )
        except Exception as exc:
            errors.append(f"{slot.slot_id}: link validation failed: {exc}")

    for tc, count in implement_by_tc.items():
        if count > 1:
            errors.append(f"TC {tc}: {count} implement slots (max 1)")

    all_tcs = {slot.target_tc for slot in slots}
    missing_analyze = sorted(all_tcs - analyze_tcs)
    if missing_analyze:
        errors.append(f"TCs without analyze slot in catalog: {missing_analyze[:10]}{'...' if len(missing_analyze)>10 else ''}")

    if errors:
        print(json.dumps({"status": "FAILED", "errors": errors}, ensure_ascii=False, indent=2))
        return 1

    print(
        json.dumps(
            {
                "status": "OK",
                "total_slots": len(slots),
                "collections": {k: len(v) for k, v in grouped.items()},
                "primary_actions": dict(Counter(s.primary_action for s in slots)),
                "secondary_action_uses": dict(
                    Counter(a for s in slots for a in s.secondary_actions)
                ),
                "analyze_tc_count": len(analyze_tcs),
                "recognize_primary": recognize_primary,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())


