#!/usr/bin/env python3
"""Audit Pascal student flow for all 102 catalog slots (UI readiness)."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.pascal.catalog.pascal_curriculum_v2_catalog import all_pedagogical_slots  # noqa: E402
from application.curriculum.pascal.showcase.pascal_showcase_core import with_resolved_pattern  # noqa: E402
from application.curriculum.pascal.showcase.pascal_showcase_registry import PASCAL_SHOWCASE_COLLECTIONS  # noqa: E402

KNOWN_SOURCE_LANGUAGES = frozenset({"python", "cpp", "java", "csharp", "javascript", "js"})
OUTPUT_JSON = Path(__file__).with_name("pascal_student_flow_audit.json")
OUTPUT_CSV = Path(__file__).with_name("pascal_student_flow_audit.csv")


def _has_text(value: object) -> bool:
    return bool(str(value or "").strip())


def _known_langs(extra: dict) -> list[str]:
    variants = extra.get("known_language_variants")
    if isinstance(variants, dict):
        return [
            lang
            for lang in KNOWN_SOURCE_LANGUAGES
            if lang in variants and _has_text((variants.get(lang) or {}).get("source_code"))
        ]
    source = str(extra.get("source_language") or "").lower()
    return [source] if source in KNOWN_SOURCE_LANGUAGES else []


def _audit_row(slot, task_id: int | None) -> dict:
    spec = with_resolved_pattern(slot.to_task_spec())
    extra = dict(spec.extra or {})
    action = slot.primary_action
    known_langs = _known_langs(extra)
    has_known = len(known_langs) > 0
    pascal_code = extra.get("code_examples_pascal") or extra.get("starter_pascal") or ""
    has_pascal = _has_text(pascal_code)
    has_instruction = _has_text(slot.short_instruction) and _has_text(slot.description)

    if action == "analyze":
        has_editor = True
        has_language_bar = False
    elif action in {"debug", "implement"}:
        has_language_bar = has_known or True
        has_editor = has_pascal if action == "debug" else True
    elif action == "translate":
        has_language_bar = has_known
        has_editor = has_known
    elif action == "assemble":
        has_language_bar = has_known or True
        has_editor = bool(extra.get("blocks") or extra.get("template"))
    else:
        has_language_bar = has_known
        has_editor = has_pascal or has_known

    issues: list[str] = []
    if action == "analyze" and not has_pascal:
        issues.append("missing_analyze_reference")
    if action == "analyze" and not _has_text(extra.get("test_cases", [{}])[0].get("output")):
        issues.append("missing_expected_output")
    if action == "debug" and not has_pascal:
        issues.append("missing_debug_starter")
    if action == "translate" and not has_known:
        issues.append("missing_known_language")
    if action == "implement" and not has_instruction:
        issues.append("missing_instruction")

    status = "ok" if not issues else "broken"

    return {
        "task_id": task_id,
        "slot_id": slot.slot_id,
        "title": spec.title_suffix,
        "collection": slot.collection_key,
        "action": action,
        "target_tc": slot.target_tc,
        "has_language_bar": has_language_bar,
        "has_pascal_editor_or_answer_field": has_editor,
        "has_valid_instruction": has_instruction,
        "known_languages": known_langs,
        "status": status,
        "issues": issues,
    }


def _resolve_task_ids(session) -> dict[str, int]:
    from application.curriculum.pascal.showcase.pascal_showcase_core import find_showcase_task_by_slug

    mapping: dict[str, int] = {}
    for slot in all_pedagogical_slots():
        spec = with_resolved_pattern(slot.to_task_spec())
        row = find_showcase_task_by_slug(session, spec.slug)
        if row is not None:
            mapping[slot.slot_id] = int(row.id)
    return mapping


def run_audit(session=None) -> list[dict]:
    task_ids: dict[str, int] = {}
    if session is not None:
        task_ids = _resolve_task_ids(session)

    rows: list[dict] = []
    for index, slot in enumerate(all_pedagogical_slots(), start=1):
        task_id = task_ids.get(slot.slot_id, index)
        rows.append(_audit_row(slot, task_id))
    return rows


def main() -> None:
    session = None
    try:
        from infrastructure.db.session import SessionLocal

        session = SessionLocal()
        # Probe connection; fall back to catalog-only audit when DB is unavailable.
        session.connection()
    except Exception:
        session = None

    rows = run_audit(session)
    if session is not None:
        session.close()
    broken = [row for row in rows if row["status"] != "ok"]

    OUTPUT_JSON.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "task_id",
                "slot_id",
                "title",
                "collection",
                "action",
                "target_tc",
                "has_language_bar",
                "has_pascal_editor_or_answer_field",
                "has_valid_instruction",
                "status",
                "issues",
            ],
        )
        writer.writeheader()
        for row in rows:
            out = {k: row[k] for k in writer.fieldnames}
            out["issues"] = ";".join(row["issues"])
            writer.writerow(out)

    print(f"Audited {len(rows)} slots across {len(PASCAL_SHOWCASE_COLLECTIONS)} collections")
    print(f"OK: {len(rows) - len(broken)} | Broken: {len(broken)}")
    print(f"JSON: {OUTPUT_JSON}")
    print(f"CSV:  {OUTPUT_CSV}")
    if broken:
        print("\nBroken slots:")
        for row in broken[:20]:
            print(f"  - {row['slot_id']} ({row['action']}): {', '.join(row['issues'])}")
        if len(broken) > 20:
            print(f"  ... and {len(broken) - 20} more")


if __name__ == "__main__":
    main()


