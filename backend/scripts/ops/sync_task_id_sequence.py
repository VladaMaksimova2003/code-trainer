"""One-off: align task.id sequence with MAX(id) after seed scripts."""
from __future__ import annotations

from infrastructure.db.init_db import init_db
from infrastructure.db.schema_align import align_task_id_sequence
from infrastructure.db.session import engine


def main() -> None:
    init_db()
    align_task_id_sequence(engine)
    print("task.id sequence synced to MAX(id).")


if __name__ == "__main__":
    main()
