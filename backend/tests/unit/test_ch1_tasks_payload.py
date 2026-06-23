"""Chapter-1 task payload integrity."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[2]
SCRIPTS = BACKEND / "scripts"


def test_ch1_payload_validation_script_passes():
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "validate_ch1_tasks.py")],
        capture_output=True,
        text=True,
        check=False,
        cwd=str(BACKEND),
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
