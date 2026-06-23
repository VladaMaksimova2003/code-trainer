#!/usr/bin/env python3
"""Report pitfall_id coverage across v192-B catalog (stage 13)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
SCRIPTS = BACKEND / "scripts"
for path in (BACKEND, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from application.curriculum.display.pitfall_catalog import PITFALLS  # noqa: E402
from application.curriculum.display.v128_transfer_meta import (  # noqa: E402
    list_v128_patterns_with_pitfall,
    resolve_v128_transfer_meta,
)

HIGH_PRIORITY: tuple[str, ...] = (
    "integer_division",
    "index_1based",
    "for_range_off_by_one",
    "round_semantics",
    "list_vs_static_array",
    "exception_model",
)


def collect_bindings() -> dict[str, list[str]]:
    by_pitfall: dict[str, list[str]] = {}
    for pattern in list_v128_patterns_with_pitfall():
        meta = resolve_v128_transfer_meta(pattern)
        pid = str(meta.get("pitfall_id") or "").strip()
        if not pid:
            continue
        by_pitfall.setdefault(pid, []).append(pattern)
    return by_pitfall


def run_validation(*, strict_high_priority: bool = True) -> int:
    bindings = collect_bindings()
    all_ids = sorted(PITFALLS.keys())
    bound_ids = sorted(bindings.keys())
    unbound = [pid for pid in all_ids if pid not in bindings]

    print(f"PITFALLS catalog entries: {len(all_ids)}")
    print(f"Bound pitfall_id values: {len(bound_ids)}")
    print(f"Patterns with pitfall: {sum(len(v) for v in bindings.values())}")

    missing_high = [pid for pid in HIGH_PRIORITY if pid not in bindings]
    if missing_high:
        print(f"High-priority unbound: {missing_high}")
    else:
        print(f"High-priority bound ({len(HIGH_PRIORITY)}/{len(HIGH_PRIORITY)}): OK")

    if unbound:
        print(f"Unbound pitfall_id ({len(unbound)}): {', '.join(unbound)}")

    errors: list[str] = []
    if strict_high_priority and missing_high:
        errors.append(f"high-priority pitfalls without slots: {missing_high}")

    if errors:
        print("ERRORS:")
        for line in errors:
            print(f"  - {line}")
        return 1

    print("OK: pitfall coverage gate passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Pitfall coverage report (v192-B)")
    parser.add_argument(
        "--allow-unbound-high-priority",
        action="store_true",
        help="Do not fail when high-priority pitfalls lack slot bindings",
    )
    args = parser.parse_args()
    return run_validation(strict_high_priority=not args.allow_unbound_high_priority)


if __name__ == "__main__":
    raise SystemExit(main())
