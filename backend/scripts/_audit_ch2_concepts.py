#!/usr/bin/env python3
from __future__ import annotations

import importlib
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
SCRIPTS = BACKEND / "scripts"
for p in (BACKEND, SCRIPTS):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from application.curriculum.content.algo_syntax_task_extra import ALGO_SYNTAX_META  # noqa: E402
from application.curriculum.content.v4_code_format import format_reference_code  # noqa: E402
from application.curriculum.validation.expected_concept_checker import (  # noqa: E402
    build_display_expected_concept_cards,
    detect_expected_concepts_in_code,
    missing_expected_concept_messages,
    prune_expected_concepts_for_code,
)
from branches_ch2_user_payload import build_tasks  # noqa: E402

LANGS = ["pascal", "python", "cpp", "csharp", "java"]


def _code(mod, lang: str, kind: str) -> str:
    if kind == "debug":
        attr = {
            "pascal": "FIXED_PASCAL",
            "python": "FIXED_PYTHON",
            "cpp": "FIXED_CPP",
            "csharp": "FIXED_CSHARP",
            "java": "FIXED_JAVA",
        }[lang]
    else:
        attr = {
            "pascal": "PASCAL",
            "python": "PYTHON",
            "cpp": "CPP",
            "csharp": "CSHARP",
            "java": "JAVA",
        }[lang]
    return format_reference_code(getattr(mod, attr), lang)


def main() -> None:
    tasks = build_tasks()
    sets: dict[str, tuple[str, ...]] = {}
    for t in tasks:
        pid = t["pattern_id"]
        kind = t["kind"]
        mod = importlib.import_module(f"ch2_user_codes.{pid}")
        meta = ALGO_SYNTAX_META.get(pid) or {}
        ec = meta.get("expected_concepts") or {}
        print(f"=== {pid} | {t['title']} ===")
        for lang in LANGS:
            code = _code(mod, lang, kind)
            detected = detect_expected_concepts_in_code(code, language=lang)
            cat = list(ec.get(lang) or [])
            pruned = prune_expected_concepts_for_code(cat, code, lang) if cat else []
            missing = missing_expected_concept_messages(code, pruned, language=lang) if pruned else []
            display = build_display_expected_concept_cards(pruned)
            tc_ids = tuple(c["id"] for c in display)
            sets[f"{pid}:{lang}"] = tc_ids
            print(f"  {lang}: detected={detected}")
            print(f"         concepts={pruned}")
            print(f"         display={list(tc_ids)}")
            if missing:
                print(f"         MISSING: {missing}")
            removed = [x for x in cat if x not in pruned]
            if removed:
                print(f"         REMOVE from catalog: {removed}")
        print()

    unique = {v for v in sets.values()}
    print(f"Unique display-TC sets: {len(unique)} / {len(sets)} total pairs")
    from collections import Counter

    dup = Counter(sets.values())
    for tc_set, count in dup.most_common():
        if count > 1:
            keys = [k for k, v in sets.items() if v == tc_set]
            print(f"  DUPLICATE x{count}: {list(tc_set)} -> {keys}")


if __name__ == "__main__":
    main()
