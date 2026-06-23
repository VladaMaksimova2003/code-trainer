import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from infrastructure.db.session import SessionLocal
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.models.task.registry import load_models
from application.tasks.services.authoring_expected_concepts import resolve_authoring_expected_concepts_by_language
load_models()
s = SessionLocal()
for tid in [129, 130, 131]:
    t = s.get(TaskModel, 130)
    t = s.get(TaskModel, tid)
    ce = t.code_examples or {}
    by = resolve_authoring_expected_concepts_by_language(ce)
    print("task", tid, "by_lang keys", list(by.keys()))
    print("  python", by.get("python"))
    print("  pascal", by.get("pascal"))
s.close()
