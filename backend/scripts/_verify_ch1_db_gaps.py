#!/usr/bin/env python3
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from application.curriculum.content.ch1_fragment_assembly import gap_count_for_template
from application.tasks.use_cases.block_reorder.get import get_block_reorder_public_task
from infrastructure.db.session import SessionLocal
from infrastructure.db.models.task.registry import load_models
from application.curriculum.mirror.pedagogical_task_store import iter_showcase_tasks

load_models()
session = SessionLocal()
out = []
for row, showcase in iter_showcase_tasks(session):
    if str(showcase.get("collection_key") or "") != "algo_basics":
        continue
    slot = str(showcase.get("slot_id") or "")
    if not slot.startswith("pas_00") and slot != "pas_008":
        continue
    if int(slot.split("_")[1]) > 8:
        continue
    payload = get_block_reorder_public_task(session, int(row.id))
    if not payload:
        continue
    pascal = dict((payload.get("language_variants") or {}).get("pascal") or {})
    template = str(pascal.get("template") or payload.get("template") or "")
    out.append({
        "id": row.id,
        "slot": slot,
        "pattern": showcase.get("slot_pattern_id"),
        "format": showcase.get("task_format"),
        "pascal_gaps": gap_count_for_template(template),
        "correct_order": pascal.get("correct_order") or payload.get("correct_order"),
    })
session.close()
print(json.dumps(out, ensure_ascii=False, indent=2))
