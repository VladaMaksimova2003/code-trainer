#!/usr/bin/env python3
import json
import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

from infrastructure.db.session import SessionLocal
from infrastructure.db.models.task.registry import load_models
from application.curriculum.mirror.pedagogical_task_store import iter_showcase_tasks

load_models()
session = SessionLocal()
rows = []
for row, showcase in iter_showcase_tasks(session):
    ck = str(showcase.get("collection_key") or "")
    if ck != "algo_basics":
        continue
    rows.append({
        "id": row.id,
        "title": row.title[:50],
        "task_num": showcase.get("task_num"),
        "slot_id": showcase.get("slot_id"),
        "pattern": showcase.get("slot_pattern_id"),
        "format": showcase.get("task_format"),
    })
session.close()
print(json.dumps(rows, ensure_ascii=False, indent=2))
