#!/usr/bin/env python3
"""Seed PostgreSQL defense stand with chosen scope (128 MVP or 192-B full).

Recommended for defense: --scope 128 (MVP core, 8 tasks per chapter).

Usage:
  cd backend
  poetry run python scripts/seed_defense_stand.py --dry-run
  poetry run python scripts/seed_defense_stand.py --scope 192 --force-catalog-sync
  poetry run python scripts/seed_defense_stand.py --scope 128 --force-catalog-sync

Requires CURRICULUM__CATALOG_SYNC_ENABLED=true or --force-catalog-sync.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
SCRIPTS = BACKEND / "scripts"


def _run_step(label: str, cmd: list[str], *, dry_run: bool) -> int:
    print(f"\n=== {label} ===")
    if dry_run:
        print("  (dry-run)", " ".join(cmd))
        return 0
    result = subprocess.run(cmd, cwd=BACKEND)
    ok = result.returncode == 0
    print(f"{'OK' if ok else 'FAIL'}: {label}")
    return result.returncode


def run_seed(*, scope: str, dry_run: bool, force_catalog_sync: bool) -> int:
    from course_scope import parse_scope, scope_report

    parsed = parse_scope(scope)
    info = scope_report(parsed)
    print(
        f"Defense stand seed: scope={parsed} "
        f"({info['target_tasks']} unified tasks, demo: {len(info['demo_slots'])} slots)"
    )
    if parsed == "128":
        print(
            "Note: expansion demo slots (pas_131, pas_147, pas_163) are excluded; "
            "use pas_006–pas_128 for MPLT demo."
        )

    force_flag = ["--force-catalog-sync"] if force_catalog_sync else []
    exit_code = 0

    steps: list[tuple[str, list[str]]] = [
        (
            "Full reseed (5 languages, catalog rows)",
            [sys.executable, str(SCRIPTS / "reseed_v4_all.py"), *force_flag],
        ),
        (
            "Pitfall -> Construction library",
            [sys.executable, str(SCRIPTS / "seed_pitfall_constructions.py"), *force_flag],
        ),
    ]

    if parsed == "128":
        steps.append(
            (
                "Trim DB to v128 core (delete task.id > 128)",
                [
                    sys.executable,
                    str(SCRIPTS / "purge_showcase_tasks_above_id.py"),
                    "--max-id",
                    "128",
                ],
            )
        )

    steps.append(
        (
            f"Validate catalog scope {parsed}",
            [sys.executable, str(SCRIPTS / "validate_course_scope.py"), "--scope", parsed],
        ),
    )

    if not dry_run:
        steps.append(
            (
                f"Validate DB scope {parsed}",
                [
                    sys.executable,
                    str(SCRIPTS / "validate_course_scope.py"),
                    "--scope",
                    parsed,
                    "--check-db",
                ],
            )
        )

    for label, cmd in steps:
        code = _run_step(label, cmd, dry_run=dry_run)
        if code:
            exit_code = code
            if not dry_run:
                break

    return exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed defense stand (128 or 192-B)")
    parser.add_argument(
        "--scope",
        default="128",
        choices=["128", "192"],
        help="128 = MVP core, 8 tasks per chapter (default); 192 = full 192-B expansion",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print steps without executing")
    from scripts.catalog_sync_guard import add_force_catalog_sync_argument, ensure_catalog_sync_allowed

    add_force_catalog_sync_argument(parser)
    args = parser.parse_args()

    if not args.dry_run and not ensure_catalog_sync_allowed(force=args.force_catalog_sync):
        return 2

    return run_seed(
        scope=args.scope,
        dry_run=args.dry_run,
        force_catalog_sync=args.force_catalog_sync,
    )


if __name__ == "__main__":
    raise SystemExit(main())
