from sqlalchemy.orm import configure_mappers

from infrastructure.db.schema_align import (
    align_admin_schema,
    align_learning_schema,
    align_profile_schema,
    align_submission_user_id,
    align_task_id_sequence,
)
from infrastructure.db.session import engine
from infrastructure.db.models.base import Base
from infrastructure.db.models.task.registry import load_models

_DB_INITIALIZED = False


def init_db() -> None:
    global _DB_INITIALIZED
    if _DB_INITIALIZED:
        return

    load_models()
    configure_mappers()
    Base.metadata.create_all(bind=engine)
    try:
        align_submission_user_id(engine)
    except Exception as exc:
        print(f"[startup] align_submission_user_id failed: {exc}", flush=True)
    try:
        align_admin_schema(engine)
    except Exception as exc:
        print(f"[startup] align_admin_schema failed: {exc}", flush=True)
    try:
        align_learning_schema(engine)
    except Exception as exc:
        print(f"[startup] align_learning_schema failed: {exc}", flush=True)
    try:
        align_profile_schema(engine)
    except Exception as exc:
        print(f"[startup] align_profile_schema failed: {exc}", flush=True)
    try:
        align_task_id_sequence(engine)
    except Exception as exc:
        print(f"[startup] align_task_id_sequence failed: {exc}", flush=True)

    _DB_INITIALIZED = True
