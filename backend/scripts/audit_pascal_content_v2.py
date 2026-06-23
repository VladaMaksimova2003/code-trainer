#!/usr/bin/env python3
"""Content audit for Pascal curriculum v2 — catalog + optional DB."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict

from application.curriculum.pascal.catalog.pascal_curriculum_v2_catalog import (
    COLLECTION_TARGETS,
    all_pedagogical_slots,
    slots_by_collection,
)
from application.curriculum.pascal.showcase.pascal_showcase_core import (
    find_showcase_task_by_slug,
    list_showcase_tasks_for_collection,
    with_resolved_pattern,
)
from application.curriculum.pascal.showcase.pascal_showcase_registry import PASCAL_SHOWCASE_COLLECTIONS

BAD_TITLE_PATTERNS = [
    re.compile(r"python", re.I),
    re.compile(r"c\+\+", re.I),
    re.compile(r"\bjava\b", re.I),
    re.compile(r"c#", re.I),
    re.compile(r"csharp", re.I),
    re.compile(r"перевод\s+с", re.I),
    re.compile(r"перевод\s+", re.I),
    re.compile(r"translation", re.I),
]

KNOWN_LANGS = ("python", "cpp", "java", "csharp")


def _title_issues(title: str) -> list[str]:
    issues: list[str] = []
    for pat in BAD_TITLE_PATTERNS:
        if pat.search(title or ""):
            issues.append(pat.pattern)
    return issues


def _slot_row(slot) -> dict:
    spec = with_resolved_pattern(slot.to_task_spec())
    extra = spec.extra or {}
    variants = extra.get("known_language_variants")
    if isinstance(variants, dict):
        variant_langs = [k for k in KNOWN_LANGS if k in variants and variants[k].get("source_code")]
        variant_count = len(variant_langs)
    else:
        variant_langs = []
        variant_count = 0
        if extra.get("source_language"):
            variant_langs = [extra["source_language"]]
            variant_count = 1

    has_flowchart = spec.builder_key == "flowchart_pascal" or bool(extra.get("diagram"))
    has_hints = bool(extra.get("concept_patterns")) or slot.target_tc  # catalog always has TC

    return {
        "slot_id": slot.slot_id,
        "slug": spec.slug,
        "title": spec.title_suffix,
        "full_title": spec.title,
        "collection": slot.collection_key,
        "target_tc": slot.target_tc,
        "primary_action": slot.primary_action,
        "difficulty": slot.difficulty,
        "builder_key": spec.builder_key,
        "known_language_variants_count": variant_count,
        "known_language_variants_langs": variant_langs,
        "has_full_4_variants": variant_count == 4,
        "flowchart": has_flowchart,
        "assemble_context": bool(
            variants or extra.get("assemble_context") or extra.get("known_language_variants")
        )
        if slot.primary_action == "assemble"
        else None,
        "title_issues": _title_issues(spec.title_suffix),
    }


def audit_catalog() -> dict:
    slots = all_pedagogical_slots()
    rows = [_slot_row(s) for s in slots]

    bad_titles = [r for r in rows if r["title_issues"]]
    transfer = [r for r in rows if r["primary_action"] == "translate"]
    transfer_missing_4 = [r for r in transfer if not r["has_full_4_variants"]]
    assemble = [r for r in rows if r["primary_action"] == "assemble"]
    assemble_no_ctx = [
        r for r in assemble if not r.get("assemble_context") and r["known_language_variants_count"] < 1
    ]
    analyze = [r for r in rows if r["primary_action"] == "analyze"]

    by_tc_action: dict[tuple[str, str], list[str]] = defaultdict(list)
    by_title: dict[str, list[str]] = defaultdict(list)
    for r in rows:
        by_tc_action[(r["target_tc"], r["primary_action"])].append(r["slot_id"])
        by_title[r["title"]].append(r["slot_id"])

    dup_tc_action = {k: v for k, v in by_tc_action.items() if len(v) > 1 and k[1] in ("translate", "implement")}
    dup_titles = {k: v for k, v in by_title.items() if len(v) > 1}

    diff_by_collection: dict[str, Counter] = {}
    for key in COLLECTION_TARGETS:
        diff_by_collection[key] = Counter(
            r["difficulty"] for r in rows if r["collection"] == key
        )

    return {
        "total_slots": len(rows),
        "unique_slot_ids": len({r["slot_id"] for r in rows}),
        "bad_title_tasks": bad_titles,
        "transfer_tasks": len(transfer),
        "transfer_missing_4_variants": transfer_missing_4,
        "assemble_tasks": assemble,
        "assemble_without_context": assemble_no_ctx,
        "analyze_tasks": analyze,
        "duplicate_by_tc_and_translate_implement": {
            f"{tc}/{action}": ids for (tc, action), ids in dup_tc_action.items()
        },
        "duplicate_titles": dup_titles,
        "difficulty_by_collection": {k: dict(v) for k, v in diff_by_collection.items()},
        "all_tasks": rows,
    }


def audit_db(session) -> dict:
    db_rows: list[dict] = []
    for col in PASCAL_SHOWCASE_COLLECTIONS:
        for item in list_showcase_tasks_for_collection(session, col.chapter_key):
            task = find_showcase_task_by_slug(session, item["slug"], collection_key=col.chapter_key)
            examples = dict((task.code_examples or {}) if task else {})
            showcase = dict(examples.get("curriculum_showcase") or {})
            known = [k for k in KNOWN_LANGS if k in examples and str(examples.get(k) or "").strip()]
            db_rows.append(
                {
                    "task_id": item["task_id"],
                    "slug": item["slug"],
                    "collection": col.chapter_key,
                    "db_title": item["title"],
                    "action": item.get("action"),
                    "known_in_code_examples": known,
                    "known_count": len(known),
                    "has_concept_hints": bool(showcase.get("concept_hints_ru")),
                    "primary_action_meta": showcase.get("primary_action"),
                }
            )
    bad_db_titles = [r for r in db_rows if _title_issues(r["db_title"])]
    return {
        "db_task_count": len(db_rows),
        "bad_db_titles": bad_db_titles,
        "transfer_in_db_missing_variants": [
            r for r in db_rows if r["action"] == "translate" and r["known_count"] < 4
        ],
        "db_tasks": db_rows,
    }


def main() -> int:
    include_db = "--db" in sys.argv
    report = {"catalog": audit_catalog()}

    if include_db:
        from infrastructure.db.models.task.registry import load_models
        from infrastructure.db.session import SessionLocal

        load_models()
        session = SessionLocal()
        try:
            report["database"] = audit_db(session)
        finally:
            session.close()

    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())


