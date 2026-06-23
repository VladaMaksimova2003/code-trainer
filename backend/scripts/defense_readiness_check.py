#!/usr/bin/env python3
"""Pre-defense readiness check for Code Trainer v192-B (stage 7).

Runs catalog validation, pitfall coverage, and a focused pytest subset.

Usage:
  cd backend
  poetry run python scripts/defense_readiness_check.py
  poetry run python scripts/defense_readiness_check.py --skip-pytest
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
SCRIPTS = BACKEND / "scripts"


def _run(label: str, cmd: list[str]) -> bool:
    print(f"\n=== {label} ===")
    result = subprocess.run(cmd, cwd=BACKEND)
    ok = result.returncode == 0
    print(f"{'OK' if ok else 'FAIL'}: {label}")
    return ok


def main() -> int:
    parser = argparse.ArgumentParser(description="Defense readiness check (v192-B)")
    parser.add_argument("--skip-pytest", action="store_true")
    args = parser.parse_args()

    checks: list[tuple[str, list[str]]] = [
        (
            "Course scope 192-B (catalog)",
            [sys.executable, str(SCRIPTS / "validate_course_scope.py"), "--scope", "192"],
        ),
        (
            "Pascal v311 catalog (192 tasks)",
            [sys.executable, str(SCRIPTS / "seed_pascal_course_v311.py"), "--validate-only"],
        ),
        (
            "Test matrix strict",
            [sys.executable, str(SCRIPTS / "validate_v128_test_matrix.py"), "--strict"],
        ),
        (
            "Pitfall catalog",
            [sys.executable, str(SCRIPTS / "validate_pitfall_catalog.py")],
        ),
        (
            "Pitfall -> Construction export (validate)",
            [sys.executable, str(SCRIPTS / "seed_pitfall_constructions.py"), "--validate-only"],
        ),
        (
            "AFCC contrast bindings",
            [sys.executable, str(SCRIPTS / "validate_afcc_contrast.py")],
        ),
        (
            "Pitfall coverage (high-priority)",
            [sys.executable, str(SCRIPTS / "validate_pitfall_coverage.py")],
        ),
        (
            "Defense demo slots (MPLT smoke)",
            [sys.executable, str(SCRIPTS / "validate_defense_demo_slots.py")],
        ),
        (
            "v128 stage-1 audit",
            [sys.executable, str(SCRIPTS / "audit_v128_stage1.py")],
        ),
    ]

    if not args.skip_pytest:
        checks.append(
            (
                "Pytest (MPLT + v192 stages)",
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/unit/test_v192_stage0_stage1.py",
                    "tests/unit/test_v192_stage3.py",
                    "tests/unit/test_v192_stage4.py",
                    "tests/unit/test_v192_stage5.py",
                    "tests/unit/test_pitfall_catalog_stage2.py",
                    "tests/unit/test_pitfall_construction_sync.py",
                    "tests/unit/test_atcc_idiom_engine.py",
                    "tests/unit/test_atcc_ast_carryover.py",
                    "tests/unit/test_fcc_ast_detector.py",
                    "tests/unit/test_afcc_contrast_detector.py",
                    "tests/unit/test_v192_stage6_demo.py",
                    "tests/unit/test_v192_stage7_scope.py",
                    "tests/unit/test_v192_stages_8_13.py",
                    "-q",
                    "--tb=line",
                ],
            )
        )

    failed: list[str] = []
    for label, cmd in checks:
        if not _run(label, cmd):
            failed.append(label)

    print("\n=== Summary ===")
    if failed:
        print("NOT READY:")
        for name in failed:
            print(f"  - {name}")
        return 1

    print("READY for defense demo (automated checks passed).")
    print("Next: docs/VKR_этап6_demo_сценарий.md + manual UI in VKR_этап7_защита_чеклист.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
