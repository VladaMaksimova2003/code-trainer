#!/usr/bin/env python3
"""Audit expected pedagogical concepts for all 102 Pascal slots."""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from application.curriculum.pascal.catalog.pascal_curriculum_v2_catalog import all_pedagogical_slots
from application.curriculum.pascal.showcase.pascal_showcase_core import PascalShowcaseTaskSpec, _showcase_meta, with_resolved_pattern
from application.curriculum.pascal_concept_hints import patterns_for_tc
from application.curriculum.showcase_display import enrich_pascal_showcase_hints

LEGACY_LABELS = {
    "assign": "Переменная",
    "io": "Ввод / вывод",
    "if_statement": "Условие",
    "for_loop": "Цикл",
    "loop": "Цикл",
    "function_definition": "Функция",
}


def _payload_for_slot(slot) -> dict:
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
    code_examples = {"curriculum_showcase": meta, "patterns": patterns_for_tc(spec.technical_concept_id)}
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
    return enrich_pascal_showcase_hints(
        {
            "language": "pascal",
            "target_language": "pascal",
            "code_examples": code_examples,
            "curriculum": {"language": "pascal", "technical_concept_id": spec.technical_concept_id},
            "concept_patterns": meta.get("concept_patterns"),
            "known_language_variants": meta.get("known_language_variants"),
        }
    )


def main() -> int:
    rows: list[dict] = []
    only_one: list[str] = []
    oop_legacy_variable: list[str] = []
    missing_ui: list[str] = []

    for slot in all_pedagogical_slots():
        payload = _payload_for_slot(slot)
        expected_ids = list(payload.get("expected_concept_ids") or [])
        expected_names = [c["name_ru"] for c in payload.get("expected_concepts") or []]
        detected = list(payload.get("detected_technical_concepts") or [])
        legacy_patterns = (payload.get("code_examples") or {}).get("patterns") or []
        legacy_labels = [LEGACY_LABELS.get(p, p) for p in legacy_patterns]

        row = {
            "task_id": slot.slot_id,
            "title": slot.title_suffix,
            "target_tc": slot.target_tc,
            "detected_tc": "|".join(detected),
            "shown_concepts": "|".join(expected_names),
            "shown_concept_ids": "|".join(expected_ids),
            "legacy_patterns": "|".join(legacy_patterns),
            "legacy_labels": "|".join(legacy_labels),
            "concept_count": len(expected_ids),
        }
        rows.append(row)

        if len(expected_ids) <= 1:
            only_one.append(slot.slot_id)
        if slot.target_tc.startswith(("class_", "object_", "method_", "inheritance")) or slot.target_tc in {
            "class_type",
            "object_instance",
            "method_dispatch",
            "inheritance_hierarchy",
        }:
            if legacy_patterns == ["assign"] or legacy_labels == ["Переменная"]:
                oop_legacy_variable.append(slot.slot_id)
        if not expected_ids:
            missing_ui.append(slot.slot_id)

    csv_path = BACKEND / "scripts" / "pascal_expected_concepts_audit.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    json_path = BACKEND / "scripts" / "pascal_expected_concepts_audit.json"
    json_path.write_text(
        json.dumps(
            {
                "rows": rows,
                "only_one_concept": only_one,
                "oop_shows_legacy_variable": oop_legacy_variable,
                "missing_expected_concepts": missing_ui,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("=== EXPECTED CONCEPTS AUDIT (102) ===")
    print(f"Only 1 concept: {len(only_one)}")
    print(f"OOP + legacy 'Переменная' pattern: {len(oop_legacy_variable)}")
    print(f"Missing expected concepts: {len(missing_ui)}")
    print("\nSample oop_s01:")
    sample = next(r for r in rows if r["task_id"] == "oop_s01")
    print(json.dumps(sample, ensure_ascii=False, indent=2))
    print(f"\nWrote {csv_path}")
    print(f"Wrote {json_path}")
    return 1 if missing_ui else 0


if __name__ == "__main__":
    raise SystemExit(main())


