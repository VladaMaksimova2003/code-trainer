"""C# algorithm-syntax course — 128 tasks, 16 chapters (8 per collection)."""
from __future__ import annotations

import sys
from pathlib import Path

TaskRow = tuple[str, str, str, str, str, str, str, str, str, str]

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from algo_v128_catalog import (  # noqa: E402
    V128_CHAPTER_ORDER,
    V128_CHAPTER_TITLES,
    V128_CORE_TASK_COUNT,
    build_task_rows,
)

V311_CORE_TASK_COUNT = V128_CORE_TASK_COUNT
V31_CHAPTER_TITLES = V128_CHAPTER_TITLES
V31_CHAPTER_ORDER = V128_CHAPTER_ORDER
V31_TASKS = build_task_rows("cs", include_expansion=False)

assert len(V31_TASKS) == V311_CORE_TASK_COUNT, f"Expected {V311_CORE_TASK_COUNT}, got {len(V31_TASKS)}"
