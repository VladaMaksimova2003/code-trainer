#!/usr/bin/env python3
"""Export showcase task list from docker to UTF-8 markdown file."""
import subprocess
from pathlib import Path

out = Path(__file__).resolve().parents[2] / "docs" / "PASCAL_SHOWCASE_TASKS_RU.md"
text = subprocess.check_output(
    ["docker", "exec", "-e", "PYTHONIOENCODING=utf-8", "code_trainer_dev-api-1", "python", "scripts/list_showcase_tasks_ru.py"],
    text=True,
    encoding="utf-8",
)
out.write_text(text, encoding="utf-8")
print(f"Wrote {len(text)} chars to {out}")
