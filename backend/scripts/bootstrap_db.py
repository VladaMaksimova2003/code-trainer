"""
Bootstrap PostgreSQL for production / fresh installs.

Alembic history in this repo assumes some base tables already exist (dev DBs
were often created via SQLAlchemy metadata). On an empty server database,
`alembic upgrade head` fails. This script:

  1. Creates all tables from current ORM models
  2. Applies idempotent schema_align patches
  3. Stamps Alembic to head (schema matches models + migration state)

Re-running on a populated DB is destructive — use only for first deploy or
after an explicit schema wipe.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]


def bootstrap() -> None:
    sys.path.insert(0, str(BACKEND_ROOT))

    from sqlalchemy.orm import configure_mappers

    from infrastructure.db.models.base import Base
    from infrastructure.db.models.task.registry import load_models
    from infrastructure.db.schema_align import (
        align_admin_schema,
        align_learning_schema,
        align_profile_schema,
        align_submission_user_id,
        align_task_id_sequence,
    )
    from infrastructure.db.session import engine

    load_models()
    configure_mappers()

    print(">>> Base.metadata.create_all()")
    Base.metadata.create_all(bind=engine)

    for name, fn in (
        ("align_submission_user_id", align_submission_user_id),
        ("align_admin_schema", align_admin_schema),
        ("align_learning_schema", align_learning_schema),
        ("align_profile_schema", align_profile_schema),
        ("align_task_id_sequence", align_task_id_sequence),
    ):
        try:
            fn(engine)
            print(f">>> {name} OK")
        except Exception as exc:
            print(f">>> {name} skipped: {exc}")

    cmd = [sys.executable, "-m", "alembic", "stamp", "head"]
    print(f">>> {' '.join(cmd)}")
    subprocess.run(cmd, cwd=BACKEND_ROOT, check=True)
    print("Database bootstrap complete.")


if __name__ == "__main__":
    bootstrap()
