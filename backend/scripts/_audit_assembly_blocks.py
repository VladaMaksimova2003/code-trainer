#!/usr/bin/env python3
"""Audit full-line assembly blocks for mid-token docx splits."""
from __future__ import annotations

import re
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.content.algo_syntax_task_extra import algo_assembly_payload
from application.curriculum.content.v4_assembly_builder import canonical_assembly_blocks
from scripts.algo_v128_catalog import ALGO_SYNTAX_META

_SPLIT_RE = re.compile(r"(?<=[A-Za-z0-9_])(?=[A-Za-z0-9_])")


def _boundary_looks_broken(blocks: list[str]) -> bool:
    for left, right in zip(blocks, blocks[1:]):
        if left.rstrip()[-1:].isalnum() and right.lstrip()[:1].isalnum():
            if not left.rstrip().endswith((";", "begin", "end", "end.", "do", "then")):
                return True
    return False


def main() -> int:
    issues: list[str] = []
    for key in sorted(ALGO_SYNTAX_META):
        meta = ALGO_SYNTAX_META[key]
        if meta.get("format_ru") != "сборка_программы":
            continue
        n = int(meta["task_num"])
        for lang in ("pascal", "python", "cpp", "csharp", "java"):
            impl = (meta.get("implementations") or {}).get(lang) or {}
            raw_blocks = list(impl.get("assembly_blocks") or [])
            if not raw_blocks:
                continue
            if _boundary_looks_broken(raw_blocks):
                fixed = canonical_assembly_blocks(raw_blocks, lang)
                issues.append(
                    f"task_{n:03d} {lang}: broken docx blocks {len(raw_blocks)} -> {len(fixed)}"
                )
            slot = f"{'pas' if lang == 'pascal' else {'python':'py','cpp':'cpp','csharp':'cs','java':'java'}[lang]}_{n:03d}"
            _, _, blocks, _ = algo_assembly_payload(slot, lang, task_format="сборка_программы")
            if _boundary_looks_broken(blocks):
                issues.append(f"task_{n:03d} {lang}: payload still broken ({len(blocks)} blocks)")

    print(f"assemble_full audit: {len(issues)} issues")
    for item in issues[:40]:
        print(" ", item)
    if len(issues) > 40:
        print(f"  ... and {len(issues) - 40} more")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
