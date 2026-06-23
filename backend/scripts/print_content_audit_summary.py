#!/usr/bin/env python3
"""Print human-readable content audit summary."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from scripts.audit_pascal_content_v2 import audit_catalog, audit_db
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal


def main() -> int:
    c = audit_catalog()
    load_models()
    s = SessionLocal()
    d = audit_db(s)
    s.close()

    print("=== 1. BAD TITLES IN DB (student sees these) ===")
    for t in d["bad_db_titles"]:
        short = t["db_title"].split("] ", 1)[-1]
        print(f"  {t['slug']:40} | {short}")

    print("\n=== 1b. BAD TITLES IN CATALOG (code only) ===")
    if c["bad_title_tasks"]:
        for t in c["bad_title_tasks"]:
            print(f"  {t['slug']} | {t['title']}")
    else:
        print("  (none — catalog titles OK)")

    print("\n=== 2. UNIQUENESS ===")
    print(f"  pedagogical slots: {c['total_slots']}")
    print(f"  unique slot_ids: {c['unique_slot_ids']}")
    print(f"  duplicate titles: {c['duplicate_titles'] or 'none'}")
    print(f"  duplicate translate/implement per TC: {c['duplicate_by_tc_and_translate_implement'] or 'none'}")

    print("\n=== 4. ANALYZE TASKS ({}) ===".format(len(c["analyze_tasks"])))
    for t in c["analyze_tasks"]:
        print(f"  {t['slot_id']:12} | {t['collection']:25} | {t['title']}")

    print("\n=== 5. ASSEMBLE TASKS ===")
    for t in c["assemble_tasks"]:
        if t["has_full_4_variants"]:
            ctx = "known_language_variants (python/cpp/java/csharp)"
        elif t["assemble_context"]:
            ctx = "other context"
        else:
            ctx = "MISSING — Pascal blocks only"
        print(f"  {t['slug']:30} | {t['title']}")
        print(f"    context: {ctx}")

    print("\n=== 7. DIFFICULTY BY COLLECTION ===")
    for col, counts in c["difficulty_by_collection"].items():
        e = counts.get("easy", 0)
        m = counts.get("medium", 0)
        h = counts.get("hard", 0)
        print(f"  {col:30} easy={e:2} medium={m:2} hard={h:2}")
    hard_total = sum(1 for t in c["all_tasks"] if t["difficulty"] == "hard")
    print(f"  TOTAL hard: {hard_total}")

    print("\n=== 6. HINTS ===")
    print(f"  in DB (student API today): {sum(1 for t in d['db_tasks'] if t['has_concept_hints'])}/102")
    print(f"  flowchart tasks in catalog: {sum(1 for t in c['all_tasks'] if t['flowchart'])}")

    print("\n=== 8. FULL TABLE (catalog) ===")
    print("slot_id;slug;collection;title;action;difficulty;variants;flowchart")
    for t in c["all_tasks"]:
        print(
            f"{t['slot_id']};{t['slug']};{t['collection']};{t['title']};"
            f"{t['primary_action']};{t['difficulty']};{t['known_language_variants_count']};"
            f"{'yes' if t['flowchart'] else 'no'}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
