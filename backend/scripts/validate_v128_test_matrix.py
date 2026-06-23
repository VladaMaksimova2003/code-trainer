#!/usr/bin/env python3
"""Validate v128 tagged test matrices after overlays."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
SCRIPTS = BACKEND / "scripts"
for path in (BACKEND, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from v128_test_matrix import is_placeholder_test  # noqa: E402
from v128_test_overlays import overlay_validation_errors  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate v128 test matrices")
    parser.add_argument("--strict", action="store_true", help="Fail on any validation error")
    args = parser.parse_args()

    from algo_v128_catalog import ALGO_SYNTAX_META  # noqa: WPS433

    errors = overlay_validation_errors(ALGO_SYNTAX_META)
    tag_hist: Counter[str] = Counter()
    placeholder_tasks = 0
    test_counts: Counter[int] = Counter()

    for pattern in sorted(ALGO_SYNTAX_META):
        tests = ALGO_SYNTAX_META[pattern].get("test_cases") or []
        test_counts[len(tests)] += 1
        if tests and all(is_placeholder_test(t) for t in tests):
            placeholder_tasks += 1
        for t in tests:
            tag_hist[str(t.get("tag") or "?")] += 1

    print(f"Tasks: {len(ALGO_SYNTAX_META)}")
    print(f"Placeholder-only tasks: {placeholder_tasks}")
    print(f"Test count histogram: {dict(sorted(test_counts.items()))}")
    print(f"Tag usage (top): {dict(tag_hist.most_common(8))}")
    print(f"Matrix validation errors: {len(errors)}")

    if errors:
        for pattern, probs in sorted(errors.items())[:20]:
            print(f"  {pattern}: {', '.join(probs)}")
        if len(errors) > 20:
            print(f"  ... and {len(errors) - 20} more")

    if placeholder_tasks:
        return 1
    if args.strict and errors:
        return 1
    if errors:
        print("WARN: non-blocking matrix issues (use --strict to fail CI)")
    else:
        print("OK: all v128 test matrices pass structural validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
