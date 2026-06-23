import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from infrastructure.db.session import SessionLocal
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.models.task.registry import load_models
load_models()
s = SessionLocal()
t = s.get(TaskModel, 130)
ce = t.code_examples or {}
show = ce.get("curriculum_showcase") or {}
print("target", show.get("target_language"))
print("expected", json.dumps(ce.get("expected_concepts"), ensure_ascii=False, indent=2)[:2000])
print("showcase ec", show.get("expected_concept_ids"))
cur = ce.get("curriculum") or {}
print("patterns", ce.get("patterns"))
s.close()
