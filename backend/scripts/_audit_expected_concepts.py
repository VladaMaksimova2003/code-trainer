#!/usr/bin/env python3
"""Audit (and optionally prune) per-language expected concepts vs reference code."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from application.curriculum.validation.expected_concept_checker import (  # noqa: E402
    missing_expected_concept_messages,
    prune_expected_concepts_for_code,
)

LANG_KEYS = ["pascal", "python", "cpp", "csharp", "java"]


def _load_tasks(json_path: Path) -> list[dict]:
    raw = json.loads(json_path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict) and isinstance(raw.get("tasks"), list):
        return raw["tasks"]
    raise SystemExit(f"Unsupported JSON shape: {json_path}")


def audit_tasks(tasks: list[dict]) -> tuple[list[str], dict[str, int]]:
    from application.curriculum.content.v4_code_format import format_reference_code

    lines: list[str] = []
    removed_counts: dict[str, int] = defaultdict(int)

    for task in sorted(tasks, key=lambda item: int(item.get("task_num") or 0)):
        task_num = int(task.get("task_num") or 0)
        pattern = str(task.get("pattern_id") or f"task_{task_num:03d}")
        title = str(task.get("title") or "").strip()
        refs = task.get("reference_codes") or {}
        concepts_by_lang = task.get("expected_concepts") or {}

        for lang in LANG_KEYS:
            raw_code = str(refs.get(lang) or "").strip()
            code = format_reference_code(raw_code, lang).strip() if raw_code else ""
            concepts = [str(item).strip() for item in concepts_by_lang.get(lang) or [] if str(item).strip()]
            if not concepts:
                continue
            if not code:
                lines.append(f"{pattern} [{lang}] no reference code, concepts={len(concepts)}")
                continue

            missing = missing_expected_concept_messages(code, concepts, language=lang)
            if missing:
                for msg in missing:
                    concept_label = msg.split(": ", 1)[-1]
                    lines.append(f"{pattern} #{task_num} {title[:40]} [{lang}] EXTRA: {concept_label}")

            pruned = prune_expected_concepts_for_code(concepts, code, lang)
            removed = [cid for cid in concepts if cid not in pruned]
            for cid in removed:
                removed_counts[cid] += 1

    return lines, dict(sorted(removed_counts.items(), key=lambda item: (-item[1], item[0])))


def prune_tasks(tasks: list[dict]) -> int:
    from application.curriculum.content.v4_code_format import format_reference_code

    changed = 0
    for task in tasks:
        refs = task.get("reference_codes") or {}
        concepts_by_lang = dict(task.get("expected_concepts") or {})
        new_by_lang: dict[str, list[str]] = {}
        for lang in LANG_KEYS:
            raw_code = str(refs.get(lang) or "")
            code = format_reference_code(raw_code, lang).strip() if raw_code.strip() else ""
            before = [str(item).strip() for item in concepts_by_lang.get(lang) or [] if str(item).strip()]
            after = prune_expected_concepts_for_code(before, code, lang)
            new_by_lang[lang] = after
            if before != after:
                changed += 1
        task["expected_concepts"] = new_by_lang
        primary = new_by_lang.get("pascal") or next(
            (new_by_lang[lang] for lang in LANG_KEYS if new_by_lang.get(lang)),
            [],
        )
        if primary != task.get("expected_concepts_primary"):
            task["expected_concepts_primary"] = primary
            changed += 1
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit expected concepts vs reference code.")
    parser.add_argument(
        "--json",
        type=Path,
        default=BACKEND / "algo_syntax_course.json",
    )
    parser.add_argument("--prune", action="store_true", help="Write pruned concepts back to JSON")
    parser.add_argument("--regenerate", action="store_true", help="Regenerate catalog/reference artifacts")
    parser.add_argument("--limit", type=int, default=0, help="Max report lines (0 = all)")
    args = parser.parse_args()

    tasks = _load_tasks(args.json)
    if args.prune:
        changed = prune_tasks(tasks)
        args.json.write_text(json.dumps(tasks, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"pruned {changed} language/task concept lists -> {args.json}")

    report, removed_stats = audit_tasks(tasks)
    print(f"audited {len(tasks)} tasks x {len(LANG_KEYS)} languages")
    print(f"extra-concept warnings: {len(report)}")
    if removed_stats:
        print("most removed concept ids (after prune):")
        for cid, count in list(removed_stats.items())[:20]:
            print(f"  {cid}: {count}")

    limit = args.limit or len(report)
    for line in report[:limit]:
        print(line)
    if len(report) > limit:
        print(f"... and {len(report) - limit} more")

    if args.regenerate:
        scripts = Path(__file__).resolve().parent
        sys.path.insert(0, str(scripts))
        from build_algorithm_syntax_course_from_docx import (  # noqa: E402
            CHAPTER_KEYS,
            emit_algo_v128_catalog,
            emit_reference_code,
            emit_test_cases,
        )

        chapter_titles = {key: key for key in CHAPTER_KEYS}
        emit_algo_v128_catalog(tasks, chapter_titles, scripts / "algo_v128_catalog.py")
        emit_reference_code(
            tasks,
            BACKEND / "application" / "curriculum" / "content" / "v4_reference_code.py",
        )
        emit_test_cases(
            tasks,
            BACKEND / "application" / "curriculum" / "content" / "v4_test_cases.py",
        )
        print("regenerated algo_v128_catalog.py, v4_reference_code.py, v4_test_cases.py")

    return 0 if not report else 0


if __name__ == "__main__":
    raise SystemExit(main())
