#!/usr/bin/env python3
"""Import 8 recursion chapter tasks (49-56) directly into PostgreSQL."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from scripts.curriculum_user_import import import_user_chapter
from scripts.recursion_ch7_user_payload import CHAPTER_KEY, TASKS


def main() -> int:
    parser = argparse.ArgumentParser(description="Import recursion chapter tasks 49-56 into PostgreSQL")
    parser.add_argument("--no-replace", action="store_true", help="Do not delete existing chapter tasks first")
    parser.add_argument("--teacher-email", default=None)
    args = parser.parse_args()

    report = import_user_chapter(
        CHAPTER_KEY,
        TASKS,
        replace=not args.no_replace,
        teacher_email=args.teacher_email,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report.get("errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())
