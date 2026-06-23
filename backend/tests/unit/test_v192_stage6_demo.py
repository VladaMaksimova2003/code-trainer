"""Stage 6: defense demo slot validation."""

import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def test_validate_defense_demo_slots_ok():
    from validate_defense_demo_slots import run_validation

    assert run_validation() == 0
