#!/usr/bin/env python3
"""Validate pitfall catalog coverage for v128/v192 meta references."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
SCRIPTS = BACKEND / "scripts"
for path in (BACKEND, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from application.curriculum.display.algorithm_debug_catalog import validate_algorithm_debug_id  # noqa: E402
from application.curriculum.display.pitfall_catalog import (  # noqa: E402
    PITFALLS,
    validate_pitfall_id,
)
from application.curriculum.display.v128_transfer_meta import (  # noqa: E402
    list_v128_patterns_with_pitfall,
    resolve_v128_transfer_meta,
)
from algo_v128_catalog import ALGO_SYNTAX_META  # noqa: E402
from algo_v192_plan import V192_EXPANSION_INDEX  # noqa: E402


def main() -> int:
    errors: list[str] = []

    for row in V192_EXPANSION_INDEX:
        pid = row.get("pitfall_id")
        if pid and not validate_pitfall_id(str(pid)):
            errors.append(f"v192 plan: unknown pitfall_id {pid!r} in task {row.get('task_num')}")

    seen: set[str] = set()
    for pattern, meta in sorted(ALGO_SYNTAX_META.items()):
        pid = str(meta.get("pitfall_id") or "").strip()
        if pid:
            seen.add(pid)
            if not validate_pitfall_id(pid) and not validate_algorithm_debug_id(pid):
                errors.append(f"catalog meta: unknown pitfall_id {pid!r} on {pattern}")

    resolved = 0
    by_type: dict[str, list[str]] = {}
    for pattern in ALGO_SYNTAX_META:
        transfer = resolve_v128_transfer_meta(pattern)
        pid = transfer.get("pitfall_id")
        if pid:
            resolved += 1
            ttype = str(transfer.get("transfer_type") or "?")
            by_type.setdefault(ttype, []).append(f"{pattern}:{pid}")

    bound = list_v128_patterns_with_pitfall()
    bound_pitfall_ids = {
        str(resolve_v128_transfer_meta(p).get("pitfall_id") or "")
        for p in bound
    }
    unbound_high_priority = [
        pid
        for pid in (
            "integer_division",
            "index_1based",
            "round_semantics",
            "for_range_off_by_one",
            "list_vs_static_array",
            "exception_model",
        )
        if pid not in bound_pitfall_ids
    ]

    print(f"PITFALLS entries: {len(PITFALLS)}")
    print(f"Unique pitfall_id in ALGO_SYNTAX_META: {len(seen)}")
    print(f"Patterns with resolve_v128_transfer_meta pitfall: {resolved}")
    print(f"Bound patterns (explicit + meta): {len(bound)}")
    for ttype in sorted(by_type):
        print(f"  {ttype}: {len(by_type[ttype])} slots")
    if unbound_high_priority:
        print(f"NOTE: high-priority pitfalls not yet bound to any pattern: {unbound_high_priority}")

    if errors:
        print("ERRORS:")
        for line in errors:
            print(f"  - {line}")
        return 1

    print("OK: all referenced pitfall_id values exist in catalog")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
