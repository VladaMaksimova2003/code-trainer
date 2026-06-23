"""Print Universal Core merge report (before/after stats + validation)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.mirror.universal_core_validation import (
    collect_universal_core_stats,
    run_all_validations,
)
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal

load_models()


def main() -> None:
    parser = argparse.ArgumentParser(description="Universal Core merge report")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    session = SessionLocal()
    try:
        stats = collect_universal_core_stats(session)
        validation = run_all_validations(session)

        pascal_rows = stats["language_tracks_pascal"]
        python_rows = stats["language_tracks_python"]
        unified = stats["unified_tasks"]
        report = {
            "active_showcase_tasks": stats["active_showcase_tasks"],
            "unified_tasks_both_tracks": unified,
            "pedagogical_slot_count": stats["pedagogical_slot_count"],
            "mirror_pairs_total": stats["mirror_pairs_total"],
            "unmerged_pairs_count": len(stats["unmerged_pairs"]),
            "unmerged_pairs": stats["unmerged_pairs"],
            "pascal_only_tasks": stats["pascal_only_tasks"],
            "python_only_tasks": stats["python_only_tasks"],
            "language_tracks_pascal": pascal_rows,
            "language_tracks_python": python_rows,
            "manual_review": stats["manual_review"],
            "validation_errors": {k: len(v) for k, v in validation.items()},
            "validation_details": validation,
        }

        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return

        print("=== Universal Core Report ===")
        print(f"Active showcase tasks:     {report['active_showcase_tasks']}")
        print(f"Unified (pascal+python):   {report['unified_tasks_both_tracks']}")
        print(f"Unique pedagogical_slot_id: {report['pedagogical_slot_count']}")
        print(f"Mirror pairs (expected):   {report['mirror_pairs_total']}")
        print(f"Unmerged pairs:            {report['unmerged_pairs_count']}")
        print(f"Pascal-only tasks:         {report['pascal_only_tasks']}")
        print(f"Python-only tasks:         {report['python_only_tasks']}")
        print(f"Tracks pascal / python:    {pascal_rows} / {python_rows}")
        print()
        print("Validation:")
        for name, count in report["validation_errors"].items():
            status = "OK" if count == 0 else f"FAIL ({count})"
            print(f"  {name}: {status}")
        if stats["unmerged_pairs"]:
            print("\nUnmerged pairs (sample):")
            for pair in stats["unmerged_pairs"][:20]:
                print(f"  {pair['pascal']} <-> {pair['python']}")
        if stats["manual_review"]:
            print(f"\nManual review: {len(stats['manual_review'])} tasks")
    finally:
        session.close()


if __name__ == "__main__":
    main()
