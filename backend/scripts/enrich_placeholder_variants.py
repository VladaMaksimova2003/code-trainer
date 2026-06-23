#!/usr/bin/env python3
"""Persist enriched placeholder gap variants into algo_syntax_course.json."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.content.placeholder_distractors import enrich_gap_variants

COURSE_JSON = BACKEND_ROOT / "algo_syntax_course.json"
LANGUAGES = ("pascal", "python", "cpp", "csharp", "java")


def _enrich_task(task: dict[str, Any]) -> bool:
    if task.get("format_ru") != "сборка_фрагмента":
        return False
    implementations = task.get("implementations") or {}
    reference_codes = task.get("reference_codes") or {}
    changed = False
    for lang in LANGUAGES:
        impl = implementations.get(lang)
        if not isinstance(impl, dict):
            continue
        gaps = impl.get("gaps") or []
        placeholder = str(impl.get("placeholder_code") or "")
        if not gaps or "___" not in placeholder:
            continue
        ref = str(reference_codes.get(lang) or "")
        gap_list = [g for g in gaps if isinstance(g, dict)]
        for gap in gap_list:
            enriched = enrich_gap_variants(
                gap,
                all_gaps=gap_list,
                placeholder_code=placeholder,
                reference_code=ref,
                language=lang,
            )
            if enriched and enriched != list(gap.get("variants") or []):
                gap["variants"] = enriched
                changed = True
    return changed


def main() -> int:
    data = json.loads(COURSE_JSON.read_text(encoding="utf-8"))
    updated = 0
    for task in data:
        if isinstance(task, dict) and _enrich_task(task):
            updated += 1
    if updated:
        COURSE_JSON.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    print(f"Enriched placeholder variants in {updated} tasks -> {COURSE_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
