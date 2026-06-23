#!/usr/bin/env python3
"""Bootstrap resources/curriculum/python as a copy of pascal (same pattern ids)."""
from __future__ import annotations

import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "resources" / "curriculum" / "pascal"
DST = REPO / "resources" / "curriculum" / "python"


def main() -> int:
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    catalog = DST / "exercise_pattern_catalog.yaml"
    text = catalog.read_text(encoding="utf-8").replace(
        "target_language: pascal", "target_language: python", 1
    )
    catalog.write_text(text, encoding="utf-8")
    track = DST / "pascal_curriculum_track.yaml"
    track.write_text(
        track.read_text(encoding="utf-8").replace("language: pascal", "language: python"),
        encoding="utf-8",
    )
    print(f"Reset {DST}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
