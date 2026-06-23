#!/usr/bin/env python3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from application.curriculum.content.algo_syntax_task_extra import algo_assembly_payload
from application.curriculum.content.ch1_fragment_assembly import gap_count_for_template

SLOTS = [
    ("pas_001", "task_002", "сборка_фрагмента"),
    ("pas_003", "task_006", "сборка_фрагмента"),
    ("pas_007", "task_129", "сборка_фрагмента"),
]

for slot, pattern, fmt in SLOTS:
    print(f"=== {slot} {pattern} ===")
    for lang in ("pascal", "python", "cpp"):
        _o, template, _b, order = algo_assembly_payload(
            slot, lang, task_format=fmt, slot_pattern_id=pattern
        )
        print(f"  {lang}: gaps={gap_count_for_template(template)} order={order}")
