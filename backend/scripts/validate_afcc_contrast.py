#!/usr/bin/env python3
"""Validate AFCC contrast test bindings for demo slots."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
SCRIPTS = BACKEND / "scripts"
for path in (BACKEND, SCRIPTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from application.curriculum.display.afcc_contrast_detector import (  # noqa: E402
    validate_afcc_contrast_bindings,
)
from application.curriculum.display.pitfall_catalog import (  # noqa: E402
    get_pitfall,
    pitfall_ids_for_transfer_type,
)
from application.curriculum.display.v128_transfer_meta import (  # noqa: E402
    _EXPLICIT_PITFALL_BY_PATTERN,
)
from algo_v128_catalog import ALGO_SYNTAX_META  # noqa: E402
from algo_v192_plan import V192_EXPANSION_INDEX  # noqa: E402


def _expansion_pattern_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    for row in V192_EXPANSION_INDEX:
        pid = str(row.get("pitfall_id") or "").strip()
        if not pid:
            continue
        mapping[f"task_{int(row['task_num']):03d}"] = pid
    return mapping


def main() -> int:
    pattern_map = dict(_EXPLICIT_PITFALL_BY_PATTERN)
    pattern_map.update(_expansion_pattern_map())

    afcc_ids = set(pitfall_ids_for_transfer_type("AFCC"))
    bound = {pid for pid in pattern_map.values() if pid in afcc_ids and get_pitfall(pid)}

    errors = validate_afcc_contrast_bindings(
        ALGO_SYNTAX_META,
        pattern_pitfall_map=pattern_map,
    )

    print(f"AFCC pitfalls in catalog: {len(afcc_ids)}")
    print(f"Bound AFCC patterns checked: {len([p for p, pid in pattern_map.items() if pid in afcc_ids])}")

    if errors:
        print("ERRORS:")
        for line in errors:
            print(f"  - {line}")
        return 1

    print("OK: AFCC contrast indices align with test suites")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
