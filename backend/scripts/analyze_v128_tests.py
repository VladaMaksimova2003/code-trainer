#!/usr/bin/env python3
"""Analyze v128 test-case diversity, placeholders, and duplicate signatures."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
SCRIPTS = BACKEND / "scripts"
for path in (BACKEND, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

PLACEHOLDER_OUTPUTS = frozenset({"ok", "7", "excellent", "retry", "demo"})
PLACEHOLDER_INPUT_MARKERS = ("demo", "empty", "edge")


def is_placeholder_test(case: dict) -> bool:
    out = str(case.get("output") or "").strip()
    inp = str(case.get("inputs") or "")
    if out == "7" and inp.strip().startswith("3\n7\n2"):
        return True
    if out in {"ok", "excellent", "retry"} and any(m in inp for m in PLACEHOLDER_INPUT_MARKERS):
        return True
    if out == "7" and "3\n7\n2" in inp:
        return True
    return False


def input_profile(inputs: str) -> dict[str, int | bool]:
    lines = [ln for ln in inputs.strip().split("\n") if ln != ""]
    nums = []
    for ln in lines:
        for tok in ln.split():
            try:
                nums.append(int(tok))
            except ValueError:
                pass
    return {
        "line_count": len(lines),
        "has_negative": any(n < 0 for n in nums),
        "has_zero": 0 in nums,
        "min_n": min(nums) if nums else None,
        "max_n": max(nums) if nums else None,
    }


def analyze(meta: dict[str, dict]) -> dict:
    by_chapter: dict[str, list[str]] = defaultdict(list)
    issues: dict[str, list[str]] = {}
    test_count_hist = Counter()
    tag_missing = 0
    sig_counter: Counter[tuple[str, str]] = Counter()

    for pattern in sorted(meta.keys()):
        row = meta[pattern]
        chapter = str(row.get("chapter_key") or "?")
        tests = row.get("test_cases") or []
        test_count_hist[len(tests)] += 1
        problems: list[str] = []

        if not tests:
            problems.append("no_tests")
        elif all(is_placeholder_test(t) for t in tests):
            problems.append("all_placeholder")
        elif any(is_placeholder_test(t) for t in tests):
            problems.append("mixed_placeholder")

        if tests and len(tests) < 4:
            problems.append("fewer_than_four_tests")

        tagged = sum(1 for t in tests if t.get("tag") or t.get("category"))
        tag_missing += len(tests) - tagged
        if tests and tagged == 0:
            problems.append("no_tags")
        elif tests and tagged == len(tests):
            pass  # all tagged — good
        elif tests and tagged < len(tests):
            problems.append("partial_tags")

        if len(tests) == 3 and not problems:
            problems.append("only_three_tests")

        for t in tests:
            sig = (str(t.get("inputs") or "")[:24], str(t.get("output") or ""))
            sig_counter[sig] += 1

        if problems:
            issues[pattern] = problems
            by_chapter[chapter].append(pattern)

    dup_sigs = [(sig, cnt) for sig, cnt in sig_counter.items() if cnt >= 4]

    return {
        "task_total": len(meta),
        "tasks_with_issues": len(issues),
        "test_count_histogram": dict(sorted(test_count_hist.items())),
        "tests_without_tag": tag_missing,
        "duplicate_signatures_4plus": sorted(dup_sigs, key=lambda x: -x[1])[:15],
        "issues_by_chapter": {ch: len(rows) for ch, rows in sorted(by_chapter.items())},
        "issue_breakdown": Counter(p for probs in issues.values() for p in probs),
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze v128 test case quality")
    parser.add_argument("--json", type=Path, help="Write full report JSON")
    args = parser.parse_args()

    from algo_v128_catalog import ALGO_SYNTAX_META  # noqa: WPS433

    report = analyze(ALGO_SYNTAX_META)
    print(f"Tasks: {report['task_total']}, with issues: {report['tasks_with_issues']}")
    print(f"Test count histogram: {report['test_count_histogram']}")
    print(f"Tests without tag/category: {report['tests_without_tag']}")
    print("Issue breakdown:", dict(report["issue_breakdown"]))
    print("Issues by chapter:", report["issues_by_chapter"])
    print("Top duplicate signatures (count >= 4):")
    for sig, cnt in report["duplicate_signatures_4plus"][:10]:
        print(f"  {cnt}x in={sig[0]!r} out={sig[1]!r}")

    if args.json:
        payload = dict(report)
        payload["issue_breakdown"] = dict(payload["issue_breakdown"])
        args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
