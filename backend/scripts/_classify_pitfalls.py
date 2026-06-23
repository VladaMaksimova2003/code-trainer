#!/usr/bin/env python3
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
from application.curriculum.display.pitfall_pair_hints import PITFALL_PAIR_HINTS
from application.curriculum.display.chapter_proactive_hints import _CHAPTER_PAIR_HINTS

rows = []
for pat, pid in sorted(_EXPLICIT_PITFALL_BY_PATTERN.items()):
    meta = ALGO_SYNTAX_META.get(pat, {})
    resolved = resolve_v128_transfer_meta(pat)
    action = pattern_action(pat)
    rows.append(
        {
            "pattern": pat,
            "title": meta.get("title") or meta.get("raw_title"),
            "pitfall_id": pid,
            "action": action,
            "chapter": meta.get("chapter_key"),
            "catalog_transfer_type": PITFALLS[pid]["transfer_type"],
            "resolved_transfer_type": resolved.get("transfer_type"),
            "action_default_tt": default_transfer_type_for_action(action),
        }
    )

out = {
    "pitfall_count": len(PITFALLS),
    "pitfall_ids": sorted(PITFALLS.keys()),
    "pair_hint_pitfalls": sorted(PITFALL_PAIR_HINTS.keys()),
    "chapter_hint_chapters": list(_CHAPTER_PAIR_HINTS.keys()),
    "explicit_pattern_bindings": rows,
    "catalog_by_type": {
        tt: [k for k, v in PITFALLS.items() if v.get("transfer_type") == tt]
        for tt in ("TCC", "ATCC", "FCC", "AFCC")
    },
}

Path(__file__).with_name("_classify_out.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2),
    encoding="utf-8",
)
