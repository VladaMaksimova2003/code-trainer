#!/usr/bin/env python3
"""Validate mirror idiom matrix, pitfall pair hints, and TC display examples."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
SCRIPTS = BACKEND / "scripts"
for path in (BACKEND, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from application.curriculum.display.mirror_idiom_matrix import (  # noqa: E402
    KNOWN_LANGS,
    _MATRIX,
    count_matrix_pairs,
    matrix_idiom_brief,
)
from application.curriculum.display.pitfall_catalog import (  # noqa: E402
    PITFALLS,
    pitfall_applies_to_language_pair,
)
from application.curriculum.display.pitfall_pair_hints import PITFALL_PAIR_HINTS  # noqa: E402

REGISTRY_PATH = BACKEND / "resources/curriculum/tc_display_registry.json"
EXPECTED_PAIRS_PER_CONCEPT = len(KNOWN_LANGS) * (len(KNOWN_LANGS) - 1)

REVERSE_SMOKE: tuple[tuple[str, str, str], ...] = (
    ("pascal", "cpp", "program_entry"),
    ("cpp", "java", "program_entry"),
    ("java", "python", "arithmetic_ops"),
    ("csharp", "pascal", "typed_declaration"),
)


def _load_registry() -> dict:
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def check_matrix(*, strict_full_grid: bool) -> list[str]:
    errors: list[str] = []
    for concept, pairs in sorted(_MATRIX.items()):
        count = len(pairs)
        if strict_full_grid and count != EXPECTED_PAIRS_PER_CONCEPT:
            errors.append(
                f"matrix {concept}: {count} pairs, expected {EXPECTED_PAIRS_PER_CONCEPT}"
            )
        for src in KNOWN_LANGS:
            for tgt in KNOWN_LANGS:
                if src == tgt:
                    continue
                if strict_full_grid and (src, tgt) not in pairs:
                    errors.append(f"matrix {concept}: missing ({src}, {tgt})")

    for source, target, concept in REVERSE_SMOKE:
        if not matrix_idiom_brief(source, target, concept):
            errors.append(f"reverse smoke failed: {source}->{target} {concept}")

    return errors


def check_pitfall_pair_hints() -> list[str]:
    errors: list[str] = []
    for pitfall_id, pairs in PITFALL_PAIR_HINTS.items():
        spec = PITFALLS.get(pitfall_id)
        if not spec:
            errors.append(f"pitfall_pair_hints references unknown pitfall: {pitfall_id}")
            continue
        for (source, target), _text in pairs.items():
            if not pitfall_applies_to_language_pair(
                spec,
                source_language=source,
                target_language=target,
            ):
                errors.append(
                    f"pair hint unreachable: {pitfall_id} ({source}->{target}) "
                    f"not in source/target langs"
                )
    return errors


def check_tc_registry(*, min_examples: int) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    data = _load_registry()
    langs = list(data.get("languages") or [])
    for tc_id, card in sorted((data.get("tc_cards") or {}).items()):
        hints = card.get("hints_by_language") or {}
        for lang in langs:
            rows = hints.get(lang) or []
            if not rows:
                errors.append(f"tc_display_registry missing: {tc_id}/{lang}")
            elif len(rows) < min_examples:
                warnings.append(f"tc_display_registry thin: {tc_id}/{lang} ({len(rows)})")
    return errors, warnings


def run_validation(*, strict_matrix: bool, min_examples: int) -> int:
    matrix_errors = check_matrix(strict_full_grid=strict_matrix)
    pitfall_errors = check_pitfall_pair_hints()
    registry_errors, registry_warnings = check_tc_registry(min_examples=min_examples)

    print(f"Mirror matrix concepts: {len(_MATRIX)}")
    print(f"Mirror matrix pair entries: {count_matrix_pairs()}")
    print(f"Expected pairs per concept (5x4): {EXPECTED_PAIRS_PER_CONCEPT}")
    print(f"Pitfall pair hint pitfalls: {len(PITFALL_PAIR_HINTS)}")

    if registry_warnings:
        print(f"TC registry thin ({len(registry_warnings)}):")
        for line in registry_warnings[:10]:
            print(f"  - {line}")
        if len(registry_warnings) > 10:
            print(f"  … and {len(registry_warnings) - 10} more")

    all_errors = matrix_errors + pitfall_errors + registry_errors
    if all_errors:
        print("ERRORS:")
        for line in all_errors:
            print(f"  - {line}")
        return 1

    print("OK: mirror coverage gate passed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Mirror idiom / pitfall / TC coverage gate")
    parser.add_argument(
        "--allow-partial-matrix",
        action="store_true",
        help="Do not require full 20-pair grid for every matrix concept",
    )
    parser.add_argument(
        "--min-examples",
        type=int,
        default=2,
        help="Minimum examples per TC card language (default: 2)",
    )
    args = parser.parse_args()
    return run_validation(
        strict_matrix=not args.allow_partial_matrix,
        min_examples=args.min_examples,
    )


if __name__ == "__main__":
    raise SystemExit(main())
