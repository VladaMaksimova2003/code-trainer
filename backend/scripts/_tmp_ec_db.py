import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from application.curriculum.validation.expected_concept_checker import check_expected_concepts
from infrastructure.db.session import SessionLocal
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.models.task.registry import load_models
from application.tasks.services.catalog.task_catalog_orchestrator import get_task_expected_concept_ids

load_models()
code = """n = int(input())
total = 0
for _ in range(n):
    total += int(input())
print(total)"""
s = SessionLocal()
for tid in [129, 130, 131]:
    ids = get_task_expected_concept_ids(db=s, task_id=tid, language="python")
    r = check_expected_concepts(code, "python", ids)
    print("task", tid, "passed", r.passed, "missing", r.missing, "labels", r.missing_labels())
s.close()
