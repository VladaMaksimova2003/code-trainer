#!/usr/bin/env python3
"""Validate demo slots and MPLT detector smoke tests for defense (stage 6).

Usage:
  cd backend
  poetry run python scripts/validate_defense_demo_slots.py
  poetry run python scripts/validate_defense_demo_slots.py --print-script
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
SCRIPTS = BACKEND / "scripts"
for path in (BACKEND, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from application.curriculum.display.atcc_idiom_engine import detect_atcc_carryover  # noqa: E402
from application.curriculum.display.transfer_pitfall_detector import (  # noqa: E402
    detect_transfer_pitfalls,
)
from application.curriculum.display.v128_transfer_meta import resolve_v128_transfer_meta  # noqa: E402
from algo_v128_catalog import ALGO_SYNTAX_META  # noqa: E402

DEMO_SLOTS: tuple[dict[str, str], ...] = (
    {"slot": "pas_004", "pattern": "task_006", "expect_pitfall": "integer_division", "expect_type": "FCC"},
    {"slot": "pas_006", "pattern": "task_007", "expect_debug": "threshold_count", "expect_type": "TCC"},
    {"slot": "pas_008", "pattern": "task_008", "expect_pitfall": "round_semantics", "expect_type": "AFCC"},
    {"slot": "pas_012", "pattern": "task_012", "expect_debug": "branch_logic", "expect_type": "TCC"},
    {"slot": "pas_020", "pattern": "task_020", "expect_pitfall": "for_range_off_by_one", "expect_type": "ATCC"},
    {"slot": "pas_131", "pattern": "task_131", "expect_pitfall": "integer_division", "expect_type": "FCC"},
    {"slot": "pas_147", "pattern": "task_147", "expect_pitfall": "index_1based", "expect_type": "FCC"},
    {"slot": "pas_163", "pattern": "task_163", "expect_pitfall": "round_semantics", "expect_type": "AFCC"},
    {"slot": "pas_007", "pattern": "task_003", "expect_pitfall": "input_line_model", "expect_type": "AFCC"},
    {"slot": "pas_027", "pattern": "task_027", "expect_pitfall": "list_vs_static_array", "expect_type": "AFCC"},
    {"slot": "pas_187", "pattern": "task_187", "expect_pitfall": "exception_model", "expect_type": "ATCC"},
)

DEMO_SCRIPT = """
=== Demo-сценарий MPLT (7–10 мин) — готовые фрагменты кода ===

1) Проактив FCC — pas_004 (assemble, integer_division)
   Баннер до submit: «В Pascal для целого частного — div, не /».

2) Реактив FCC — pas_131 (expansion debug, integer_division)
   Pascal, отправить с ошибкой деления:
   writeln(total / n);

   Ожидание: TRANSFER_PITFALL (FCC, AST|lex) на вкладках «Тесты» / «Ошибки».
   Альтернатива: pas_006 (threshold_count) — buggy debug без исправления порога.

3) AFCC contrast — pas_008 (implement, round_semantics)
   Contrast-тест #2: вход 2\\n1\\n4\\n -> эталон «4 2 1» (div), Round даст «4 3 1».
   Вставить Round вместо div для среднего:
   writeln(best, ' ', round(total / n), ' ', passed);

   Ожидание: TRANSFER_PITFALL (AFCC, contrast), contrast_case_index=1.

4) ATCC — mirror Python→Pascal (pas_002 или любой implement)
   В коде Pascal оставить Python-идиому:
   print(n)

   Ожидание: CONSTRUCTION_WARNING (ATCC, AST) до/после submit.

5) Три формата в одной главе: pas_001 (TCC), pas_003 (TCC assemble), pas_012 (FCC debug).

Подробно: docs/VKR_этап6_demo_сценарий.md
"""


def _check_demo_slots() -> list[str]:
    errors: list[str] = []
    for row in DEMO_SLOTS:
        pattern = row["pattern"]
        if pattern not in ALGO_SYNTAX_META:
            errors.append(f"{row['slot']}: missing pattern {pattern} in ALGO_SYNTAX_META")
            continue
        meta = resolve_v128_transfer_meta(pattern)
        pid = str(meta.get("pitfall_id") or "")
        debug_id = str(meta.get("debug_id") or "")
        tt = str(meta.get("transfer_type") or "").upper()
        expect_pitfall = row.get("expect_pitfall")
        expect_debug = row.get("expect_debug")
        if expect_pitfall is not None and pid != expect_pitfall:
            errors.append(
                f"{row['slot']}: pitfall_id {pid!r} != expected {expect_pitfall!r}"
            )
        if expect_debug is not None and debug_id != expect_debug:
            errors.append(
                f"{row['slot']}: debug_id {debug_id!r} != expected {expect_debug!r}"
            )
        if tt != row["expect_type"]:
            errors.append(
                f"{row['slot']}: transfer_type {tt!r} != expected {row['expect_type']!r}"
            )
    return errors


def _check_contrast_cases() -> list[str]:
    errors: list[str] = []
    for pattern in ("task_008", "task_163", "task_027"):
        tests = list((ALGO_SYNTAX_META.get(pattern) or {}).get("test_cases") or [])
        if len(tests) < 1:
            errors.append(f"{pattern}: need >=1 test case for contrast")
            continue
        idx = 1 if pattern in ("task_008", "task_163") else 0
        if len(tests) <= idx:
            errors.append(f"{pattern}: need test index {idx} for contrast")
            continue
        case = tests[idx]
        if not case.get("mplt_contrast"):
            errors.append(f"{pattern}: test[{idx}] missing mplt_contrast flag")
    task3 = (ALGO_SYNTAX_META.get("task_003") or {}).get("test_cases") or []
    if task3 and not task3[0].get("mplt_contrast"):
        errors.append("task_003: contrast test[0] missing mplt_contrast")
    return errors


def _smoke_detectors() -> list[str]:
    errors: list[str] = []

    fcc = detect_transfer_pitfalls(
        pitfall_id="integer_division",
        transfer_type="FCC",
        source_language="python",
        target_language="pascal",
        code="program T; begin writeln(total / n); end.",
        test_results=[{"status": "FAILED"}],
    )
    if not fcc or fcc[0].get("transfer_type") != "FCC":
        errors.append("FCC smoke: integer_division did not fire")

    afcc = detect_transfer_pitfalls(
        pitfall_id="round_semantics",
        transfer_type="AFCC",
        source_language="python",
        target_language="pascal",
        code="program T; begin end.",
        test_results=[{"status": "PASSED"}, {"status": "FAILED"}],
    )
    if not afcc or afcc[0].get("detection") != "contrast":
        errors.append("AFCC smoke: round_semantics contrast did not fire")

    atcc = detect_atcc_carryover(
        "pascal",
        "python",
        "writeln(n)\nprint(n)\n",
        expected_concepts=["stdout_write"],
    )
    if not atcc or atcc[0].get("detection") != "ast":
        errors.append("ATCC smoke: writeln in python submission did not fire AST")

    no_afcc = detect_transfer_pitfalls(
        pitfall_id="round_semantics",
        transfer_type="AFCC",
        source_language="python",
        target_language="pascal",
        code="x",
        test_results=[{"status": "FAILED"}, {"status": "PASSED"}],
    )
    if no_afcc:
        errors.append("AFCC smoke: fired when only non-contrast test failed")

    return errors


def run_validation(*, print_script: bool = False) -> int:
    errors: list[str] = []
    errors.extend(_check_demo_slots())
    errors.extend(_check_contrast_cases())
    errors.extend(_smoke_detectors())

    print(f"Demo slots checked: {len(DEMO_SLOTS)}")
    if errors:
        print("ERRORS:")
        for line in errors:
            print(f"  - {line}")
        return 1

    print("OK: demo slots, contrast cases, MPLT detector smoke tests")
    if print_script:
        print(DEMO_SCRIPT)
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Defense demo slot validation (stage 6)")
    parser.add_argument(
        "--print-script",
        action="store_true",
        help="Print copy-paste demo walkthrough after validation",
    )
    args = parser.parse_args()
    return run_validation(print_script=args.print_script)


if __name__ == "__main__":
    raise SystemExit(main())
