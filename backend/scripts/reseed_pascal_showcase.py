"""One-off: drop Pascal showcase tasks and re-seed (dev container helper)."""
from infrastructure.db.session import SessionLocal
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.task.task import Task
from application.curriculum.pascal.legacy.loops.loops_showcase_seeder import seed_pascal_loops_showcase
from sqlalchemy import delete, select

load_models()
session = SessionLocal()
ids = list(
    session.scalars(select(Task.id).where(Task.title.like("[Pascal Loops Showcase]%"))).all()
)
if ids:
    session.execute(delete(Task).where(Task.id.in_(ids)))
    session.commit()
    print(f"deleted {len(ids)} showcase tasks")
report = seed_pascal_loops_showcase(session)
session.commit()
print(report.to_dict())

