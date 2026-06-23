#!/usr/bin/env python3
"""Validate MPLT model against project catalog."""
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))
sys.path.insert(0, str(BACKEND / "scripts"))

from application.curriculum.display.pitfall_catalog import PITFALLS
from application.curriculum.display.v128_transfer_meta import (
    ALGO_SYNTAX_META,
    _EXPLICIT_PITFALL_BY_PATTERN,
    resolve_v128_transfer_meta,
    default_transfer_type_for_action,
    pattern_action,
)
from application.curriculum.content.algo_syntax_task_extra import (
    v128_pattern_for_slot,
    _build_v128_slot_pattern_map,
)
from application.curriculum.display.chapter_proactive_hints import chapter_proactive_hint
from scripts.algo_v128_catalog import _TASK_INDEX  # noqa: E402


def all_patterns() -> list[str]:
    return sorted(ALGO_SYNTAX_META.keys())


def pitfall_concepts() -> dict[str, set[str]]:
    return {pid: set(spec.get("concept_ids") or []) for pid, spec in PITFALLS.items()}


def analyze_no_pitfall_transfer():
    """Patterns without pitfall_id but non-TCC signals."""
    rows = []
    for pat in all_patterns():
        meta = ALGO_SYNTAX_META.get(pat) or {}
        resolved = resolve_v128_transfer_meta(pat)
        pid = resolved.get("pitfall_id")
        action = pattern_action(pat)
        action_default = default_transfer_type_for_action(action)
        ec = meta.get("expected_concepts") or {}
        all_concepts = set()
        for ids in ec.values():
            if isinstance(ids, list):
                all_concepts.update(ids)
        # chapter hint exists for common pairs?
        chapter_pairs = []
        for src in ("python", "pascal", "cpp", "java", "csharp"):
            for tgt in ("python", "pascal", "cpp", "java", "csharp"):
                if src == tgt:
                    continue
                hint = chapter_proactive_hint(pat, source_language=src, target_language=tgt)
                if hint:
                    chapter_pairs.append(f"{src}->{tgt}")
        if not pid and (chapter_pairs or action_default != "TCC"):
            rows.append(
                {
                    "pattern": pat,
                    "title": meta.get("title") or meta.get("raw_title"),
                    "action": action,
                    "action_default_tt": action_default,
                    "chapter_hint_pairs": len(chapter_pairs),
                    "sample_chapter_pairs": chapter_pairs[:4],
                    "expected_concepts_count": len(all_concepts),
                }
            )
    return rows


def analyze_multi_pitfall():
    """For each pattern, which catalog pitfalls match via concept overlap."""
    pc = pitfall_concepts()
    rows = []
    for pat in all_patterns():
        meta = ALGO_SYNTAX_META.get(pat) or {}
        explicit = _EXPLICIT_PITFALL_BY_PATTERN.get(pat)
        ec = meta.get("expected_concepts") or {}
        all_concepts = set()
        for ids in ec.values():
            if isinstance(ids, list):
                all_concepts.update(ids)
        matching = []
        for pid, concepts in pc.items():
            overlap = all_concepts & concepts
            if overlap:
                matching.append(
                    {
                        "pitfall_id": pid,
                        "transfer_type": PITFALLS[pid]["transfer_type"],
                        "overlap": sorted(overlap),
                    }
                )
        if len(matching) >= 2 or (explicit and len(matching) >= 2):
            rows.append(
                {
                    "pattern": pat,
                    "title": meta.get("title") or meta.get("raw_title"),
                    "explicit_pitfall": explicit,
                    "matching_pitfalls": matching,
                }
            )
        elif explicit:
            # explicit + other matches
            others = [m for m in matching if m["pitfall_id"] != explicit]
            if others:
                rows.append(
                    {
                        "pattern": pat,
                        "title": meta.get("title") or meta.get("raw_title"),
                        "explicit_pitfall": explicit,
                        "matching_pitfalls": matching,
                        "note": "explicit + concept overlap",
                    }
                )
    return rows


def analyze_concept_implied_category():
    """Map concepts to pitfalls that reference them."""
    pc = pitfall_concepts()
    concept_to_pitfalls: dict[str, list[dict]] = {}
    for pid, concepts in pc.items():
        tt = PITFALLS[pid]["transfer_type"]
        for c in concepts:
            concept_to_pitfalls.setdefault(c, []).append({"pitfall_id": pid, "transfer_type": tt})
    multi_tt = {
        c: pits
        for c, pits in concept_to_pitfalls.items()
        if len({p["transfer_type"] for p in pits}) > 1
    }
    return concept_to_pitfalls, multi_tt


def slot_task_examples():
    slot_map = _build_v128_slot_pattern_map()
    examples = []
    for item in _TASK_INDEX[:15]:
        n = int(item["task_num"])
        pat = item["pattern_id"]
        slot = f"pas_{n:03d}"
        resolved = resolve_v128_transfer_meta(pat)
        examples.append(
            {
                "slot": slot,
                "pattern": pat,
                "mapped_pattern": slot_map.get(slot),
                "pitfall_id": resolved.get("pitfall_id"),
                "transfer_type": resolved.get("transfer_type"),
                "action": pattern_action(pat),
            }
        )
    return examples


out = {
    "total_patterns": len(all_patterns()),
    "explicit_pitfall_patterns": len(_EXPLICIT_PITFALL_BY_PATTERN),
    "no_pitfall_non_tcc_signals": analyze_no_pitfall_transfer(),
    "multi_pitfall_patterns": analyze_multi_pitfall(),
    "slot_examples": slot_task_examples(),
}

concept_map, multi_tt = analyze_concept_implied_category()
out["concepts_with_multiple_transfer_types"] = multi_tt
out["sample_concepts"] = {
    k: concept_map.get(k, [])
    for k in (
        "stdin_read",
        "exception_handling",
        "dynamic_array",
        "indexed_sequence",
        "arithmetic_ops",
        "filter_select",
    )
}

Path(__file__).with_name("_model_stress_out.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
print("written", Path(__file__).with_name("_model_stress_out.json"))
