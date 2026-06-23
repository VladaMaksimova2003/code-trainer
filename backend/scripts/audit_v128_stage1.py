#!/usr/bin/env python3
"""Audit v128 catalog quality after stage-1 overlays (placeholder tests, debug pairs)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
SCRIPTS = BACKEND / "scripts"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

PLACEHOLDER_OUTPUTS = frozenset({"ok", "7", "excellent", "retry", "demo"})
PLACEHOLDER_INPUT_MARKERS = ("demo", "empty", "edge")


def _is_placeholder_test(case: dict) -> bool:
    out = str(case.get("output") or "").strip()
    inp = str(case.get("inputs") or "")
    if out in PLACEHOLDER_OUTPUTS and out == "7" and "3\n7\n2" in inp:
        return True
    if out in {"ok", "excellent", "retry"} and any(m in inp for m in PLACEHOLDER_INPUT_MARKERS):
        return True
    if out == "7" and inp.strip().startswith("3\n7\n2"):
        return True
    return False


def audit_meta(meta: dict[str, dict]) -> dict[str, list[str]]:
    issues: dict[str, list[str]] = {}
    for pattern in sorted(meta.keys()):
        if pattern.startswith("task_"):
            try:
                num = int(pattern.split("_", 1)[1])
            except Exception:
                num = None
            if isinstance(num, int) and num > 128:
                continue
        row = meta[pattern]
        problems: list[str] = []
        tests = row.get("test_cases") or []
        if not tests:
            problems.append("no test_cases")
        elif all(_is_placeholder_test(t) for t in tests):
            problems.append("all placeholder test_cases")

        action = str(row.get("action") or "")
        if action == "debug":
            impls = row.get("implementations") or {}
            for lang in ("pascal", "python"):
                impl = impls.get(lang) or {}
                buggy = str(impl.get("buggy_code") or "").strip()
                fixed = str(impl.get("fixed_code") or "").strip()
                if not buggy or not fixed:
                    problems.append(f"debug missing buggy/fixed ({lang})")
                elif buggy == fixed:
                    problems.append(f"debug buggy==fixed ({lang})")

        refs = row.get("reference_codes") or {}
        if not any(str(refs.get(lang) or "").strip() for lang in ("pascal", "python")):
            problems.append("no reference_codes (pascal/python)")

        if problems:
            issues[pattern] = problems
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit v128 ALGO_SYNTAX_META quality")
    parser.add_argument("--json", type=Path, help="Write report JSON")
    args = parser.parse_args()

    from algo_v128_catalog import ALGO_SYNTAX_META  # noqa: WPS433

    issues = audit_meta(ALGO_SYNTAX_META)
    branches = {k: v for k, v in issues.items() if k in {f"task_{i:03d}" for i in range(9, 17)}}

    print(f"Total v128 tasks with issues: {len(issues)} / 128")
    print(f"Branches (9-16) issues: {len(branches)}")
    for pattern, probs in sorted(issues.items()):
        print(f"  {pattern}: {', '.join(probs)}")

    if args.json:
        payload = {"issue_count": len(issues), "issues": issues, "branches_issue_count": len(branches)}
        args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return 1 if branches else 0


if __name__ == "__main__":
    raise SystemExit(main())
