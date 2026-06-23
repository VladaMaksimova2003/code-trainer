#!/usr/bin/env python3
"""Report Pascal curriculum v2 slot catalog statistics."""

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


def main() -> int:
    slots = all_pedagogical_slots()
    grouped = slots_by_collection()

    by_collection: dict[str, int] = {k: len(v) for k, v in grouped.items()}
    by_primary = Counter(s.primary_action for s in slots)
    by_pattern = Counter(
        with_resolved_pattern(s.to_task_spec()).exercise_pattern_id for s in slots
    )
    secondary_total = sum(len(s.secondary_actions) for s in slots)
    secondary_by_action = Counter(
        a for s in slots for a in s.secondary_actions
    )

    tc_analyze = sorted({s.target_tc for s in slots if s.primary_action == "analyze"})
    tc_implement = {
        s.target_tc
        for s in slots
        if s.primary_action == "implement"
    }

    legacy_slugs = {
        s.task_slug
        for s in slots
        if not s.slot_id.startswith(
            (
                "vai_s",
                "cond_s",
                "loop_s",
            )
        )
        and s.task_slug == s.slot_id
    }

    report = {
        "total_tasks": len(slots),
        "target_total": sum(COLLECTION_TARGETS.values()),
        "by_collection": by_collection,
        "collection_targets": COLLECTION_TARGETS,
        "by_primary_action": dict(by_primary),
        "secondary_actions_total": secondary_total,
        "secondary_actions_by_type": dict(secondary_by_action),
        "technical_concepts_with_analyze": len(tc_analyze),
        "technical_concepts_with_implement_capstone": len(tc_implement),
        "top_patterns": dict(by_pattern.most_common(15)),
        "slot_ids_sample": [s.slot_id for s in slots[:5]],
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())


