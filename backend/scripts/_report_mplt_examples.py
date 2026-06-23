#!/usr/bin/env python3
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
SCRIPTS = BACKEND / "scripts"
sys.path.insert(0, str(SCRIPTS))

from application.curriculum.content.algo_syntax_showcase_meta import (
    enrich_student_expected_concepts,
    transfer_meta_for_language_pair,
)
from application.curriculum.display.v128_transfer_meta import resolve_v128_transfer_meta
from algo_v128_catalog import ALGO_SYNTAX_META


def chapter(pattern: str) -> str | None:
    return (ALGO_SYNTAX_META.get(pattern) or {}).get("chapter_key")


def banner_text(tr: dict) -> str:
    for key in ("pedagogy_note_ru", "reference_warning_ru", "hint_ru", "contrast_note_ru"):
        val = str(tr.get(key) or "").strip()
        if val:
            return val
    return "(none)"


cases = [
    ("pas_001", "task_002", "python", "pascal", "assemble"),
    ("pas_002", "task_001", "pascal", "python", "assemble"),
    ("pas_007", "task_003", "cpp", "java", "implement"),
    ("pas_004", "task_006", "cpp", "python", "assemble"),
    ("pas_003", "task_005", "python", "java", "assemble"),
    ("pas_005", "task_004", "cpp", "java", "debug"),
    ("pas_006", "task_007", "java", "python", "debug"),
    ("pas_008", "task_008", "python", "pascal", "implement"),
    ("pas_002", "task_001", "csharp", "java", "assemble"),
    ("pas_001", "task_002", "java", "cpp", "assemble"),
]

out = BACKEND / "scripts" / "_report_mplt_out.json"
results = []

for slot, pat, src, tgt, action in cases:
    meta = resolve_v128_transfer_meta(pat)
    tr = transfer_meta_for_language_pair(pat, source_language=src, target_language=tgt)
    payload = enrich_student_expected_concepts(
        {
            "curriculum": {"slot_id": slot, "target_language": tgt},
            "code_examples": {
                "curriculum_showcase": {
                    "slot_id": slot,
                    "target_language": tgt,
                    "known_language_variants": {src: {"source_code": "x"}},
                }
            },
        },
        pattern_key=pat,
        slot_id=slot,
        target_language=tgt,
        slot_pattern_id=pat,
    )
    cards = (payload.get("curriculum") or {}).get("expected_concepts") or []
    hints = [
        (c.get("id"), c.get("transfer_hint_ru"))
        for c in cards
        if c.get("transfer_hint_ru")
    ]
    results.append(
        {
            "slot": slot,
            "pattern": pat,
            "source_language": src,
            "target_language": tgt,
            "action": action,
            "chapter_key": chapter(pat),
            "pitfall_id": meta.get("pitfall_id"),
            "expected_concept_ids": [c.get("id") for c in cards],
            "banner": banner_text(tr),
            "chip_hints": hints,
            "transfer_meta_keys": list(tr.keys()),
        }
    )

import json

out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"wrote {out}")
