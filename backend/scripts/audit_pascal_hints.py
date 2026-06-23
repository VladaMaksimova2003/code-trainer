#!/usr/bin/env python3
"""Audit dynamic Pascal hints for all 102 pedagogical slots."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from application.curriculum.pascal.catalog.pascal_curriculum_v2_catalog import all_pedagogical_slots
from application.curriculum.pascal_hint_engine import GENERIC_BEGIN_END_ONLY
from application.curriculum.pascal.showcase.pascal_showcase_core import PascalShowcaseTaskSpec, _showcase_meta, with_resolved_pattern
from application.curriculum.showcase_display import enrich_pascal_showcase_hints

BAD_TITLE_PATTERN = re.compile(r"\b(program|integer|array|class)\b", re.I)
GENERIC_ONLY_MARKER = GENERIC_BEGIN_END_ONLY


def _hints_for_slot(slot) -> dict:
    spec = with_resolved_pattern(slot.to_task_spec())
    extra = spec.extra or {}
    full = PascalShowcaseTaskSpec(
        collection_key=spec.collection_key,
        slug=spec.slug,
        title_suffix=spec.title_suffix,
        description=spec.description,
        difficulty=spec.difficulty,
        technical_concept_id=spec.technical_concept_id,
        exercise_pattern_id=spec.exercise_pattern_id,
        assignment_type=spec.assignment_type,
        builder_key=spec.builder_key,
        extra=extra,
        slot_id=slot.slot_id,
        primary_action=slot.primary_action,
        secondary_actions=slot.secondary_actions,
        short_instruction=slot.short_instruction,
    )
    meta = _showcase_meta(full)
    code_examples = {"curriculum_showcase": meta}
    variants = extra.get("known_language_variants")
    if isinstance(variants, dict):
        for lang, entry in variants.items():
            if isinstance(entry, dict):
                code = entry.get("source_code") or entry.get("code")
                if code:
                    code_examples[str(lang).lower()] = code
    pascal = extra.get("reference_solution_pascal") or extra.get("code_examples_pascal")
    if pascal:
        code_examples["pascal"] = pascal

    payload = enrich_pascal_showcase_hints(
        {
            "language": "pascal",
            "target_language": "pascal",
            "code_examples": code_examples,
            "curriculum": {
                "language": "pascal",
                "technical_concept_id": spec.technical_concept_id,
            },
            "concept_patterns": meta.get("concept_patterns"),
            "known_language_variants": meta.get("known_language_variants"),
        }
    )
    return payload


def main() -> int:
    rows: list[dict] = []
    hint_counter: Counter[str] = Counter()
    bad_titles: list[dict] = []
    non_pascal_learning: list[dict] = []
    begin_end_only: list[dict] = []
    empty_hints: list[dict] = []

    for slot in all_pedagogical_slots():
        payload = _hints_for_slot(slot)
        hints = list(payload.get("concept_hints_ru") or [])
        transfer = payload.get("transfer_hints_by_language") or {}

        for h in hints:
            hint_counter[h] += 1

        title = slot.title_suffix
        if BAD_TITLE_PATTERN.search(title):
            bad_titles.append({"slot_id": slot.slot_id, "title": title})

        if payload.get("language") != "pascal":
            non_pascal_learning.append(
                {"slot_id": slot.slot_id, "language": payload.get("language")}
            )

        if hints == [GENERIC_ONLY_MARKER]:
            begin_end_only.append({"slot_id": slot.slot_id, "target_tc": slot.target_tc})
        if not hints:
            empty_hints.append({"slot_id": slot.slot_id, "target_tc": slot.target_tc})

        rows.append(
            {
                "slot_id": slot.slot_id,
                "title": title,
                "collection": slot.collection_key,
                "target_tc": slot.target_tc,
                "primary_action": slot.primary_action,
                "language": payload.get("language"),
                "technical_concepts": payload.get("technical_concepts"),
                "concept_hints_ru": hints,
                "transfer_langs": sorted(transfer.keys()),
            }
        )

    print("=== PASCAL HINTS AUDIT (102 slots) ===")
    print(f"Empty hints: {len(empty_hints)}")
    print(f"begin/end-only hints: {len(begin_end_only)}")
    print(f"Bad titles (program/integer/array/class): {len(bad_titles)}")
    print(f"Non-pascal learning language: {len(non_pascal_learning)}")

    if bad_titles:
        print("\n--- Bad titles ---")
        for row in bad_titles:
            print(f"  {row['slot_id']}: {row['title']}")

    if begin_end_only:
        print("\n--- begin/end-only ---")
        for row in begin_end_only:
            print(f"  {row['slot_id']} ({row['target_tc']})")

    print("\n--- Top hints ---")
    for hint, count in hint_counter.most_common(8):
        print(f"  [{count}x] {hint[:80]}")

    out = BACKEND / "scripts" / "pascal_hints_audit.json"
    out.write_text(
        json.dumps(
            {
                "rows": rows,
                "empty_hints": empty_hints,
                "begin_end_only": begin_end_only,
                "bad_titles": bad_titles,
                "non_pascal_learning": non_pascal_learning,
                "hint_frequency": dict(hint_counter),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nWrote {out}")

    failed = bool(empty_hints or begin_end_only or bad_titles or non_pascal_learning)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())


