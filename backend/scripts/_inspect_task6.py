#!/usr/bin/env python3
import json
from infrastructure.db.models.task.registry import load_models

load_models()
from application.tasks.services.block_reorder_helpers import build_entity_from_db
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.session import SessionLocal
from application.curriculum.content.algo_syntax_task_extra import algo_assembly_payload

s = SessionLocal()
t = s.query(TaskModel).filter(TaskModel.id == 6).first()
if not t:
    from infrastructure.db.models.task.task_curriculum_link import TaskCurriculumLink
    link = s.query(TaskCurriculumLink).filter(TaskCurriculumLink.slot_id == "pas_006").first()
    if link:
        t = s.query(TaskModel).filter(TaskModel.id == link.task_id).first()
print("task_id:", t.id if t else None)
print("title:", t.title)
e = build_entity_from_db(t, t.block_reorder_task)
v = e._get_variant("pascal")
print("db blocks:", v.get("blocks"))
print("db correct_order:", v.get("correct_order"))
print("db template:", (v.get("template") or "")[:250])

orig, tpl, blocks, co = algo_assembly_payload(
    "pas_006", "pascal", task_format="сборка_фрагмента"
)
print("payload blocks:", blocks)
print("payload correct_order:", co)
print("payload template:", tpl[:250])

from scripts.algo_v128_catalog import ALGO_SYNTAX_META

meta = ALGO_SYNTAX_META["task_006"]["implementations"]["pascal"]
print("gaps:", json.dumps(meta.get("gaps"), ensure_ascii=False, indent=2))
print("placeholder_code:", meta.get("placeholder_code"))
s.close()
