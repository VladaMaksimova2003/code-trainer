#!/usr/bin/env python3
"""Export compact 102-task content audit table (catalog vs DB)."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from scripts.audit_pascal_content_v2 import audit_catalog, audit_db
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal


def main() -> int:
    catalog = audit_catalog()
    load_models()
    session = SessionLocal()
    try:
        db = audit_db(session)
    finally:
        session.close()

    db_by_slug = {r["slug"]: r for r in db["db_tasks"]}
    out_path = BACKEND / "scripts" / "pascal_content_audit_102.csv"
    weak: list[dict] = []

    with out_path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.writer(fh, delimiter=";")
        writer.writerow(
            [
                "slot_id",
                "slug",
                "collection",
                "catalog_title",
                "db_title",
                "title_synced",
                "primary_action",
                "difficulty",
                "variants_catalog",
                "variants_db",
                "flowchart",
                "hints_db",
                "weak_reason",
            ]
        )
        for row in catalog["all_tasks"]:
            slug = row["slug"]
            db_row = db_by_slug.get(slug, {})
            cat_title = row["title"]
            db_title = db_row.get("db_title", "")
            synced = cat_title in db_title or db_title.endswith(cat_title)
            reasons: list[str] = []
            if row["title_issues"]:
                reasons.append("bad_catalog_title")
            if db_row and not synced:
                reasons.append("db_title_stale")
            if row["primary_action"] == "translate" and not row["has_full_4_variants"]:
                reasons.append("missing_4_variants_catalog")
            if row["primary_action"] == "translate" and db_row.get("known_count", 0) < 4:
                reasons.append("missing_4_variants_db")
            if row["primary_action"] == "assemble" and not row.get("assemble_context"):
                reasons.append("assemble_no_context")
            if row["difficulty"] != "hard" and row["primary_action"] == "implement":
                pass
            if not db_row.get("has_concept_hints"):
                reasons.append("no_hints_in_db")
            if row["title"].startswith("Program:") or "integer" in row["title"]:
                reasons.append("weak_title_style")
            if row["primary_action"] == "analyze" and "предскажите" not in row["title"].lower():
                reasons.append("analyze_title_unclear")

            weak_reason = ", ".join(reasons)
            if weak_reason:
                weak.append({**row, "weak_reason": weak_reason, "db_title": db_title})

            writer.writerow(
                [
                    row["slot_id"],
                    slug,
                    row["collection"],
                    cat_title,
                    db_title,
                    "yes" if synced else "NO",
                    row["primary_action"],
                    row["difficulty"],
                    row["known_language_variants_count"],
                    db_row.get("known_count", ""),
                    "yes" if row["flowchart"] else "no",
                    "yes" if db_row.get("has_concept_hints") else "no",
                    weak_reason,
                ]
            )

    summary = {
        "csv_path": str(out_path),
        "catalog_bad_titles": len(catalog["bad_title_tasks"]),
        "db_bad_titles": len(db["bad_db_titles"]),
        "db_stale_title_count": sum(
            1
            for row in catalog["all_tasks"]
            if not (
                db_by_slug.get(row["slug"], {}).get("db_title", "").endswith(row["title"])
            )
        ),
        "weak_task_count": len(weak),
        "hard_count": sum(1 for t in catalog["all_tasks"] if t["difficulty"] == "hard"),
        "duplicate_slots": catalog["duplicate_titles"],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
