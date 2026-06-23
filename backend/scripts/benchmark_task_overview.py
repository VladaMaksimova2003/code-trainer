"""Benchmark task list payload size and response time (before/after overview)."""

from __future__ import annotations

import json
import sys
import time
from collections.abc import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from application.tasks.services.catalog.task_catalog_orchestrator import list_task_overviews, list_tasks
from application.tasks.services.catalog.task_overview import list_task_overviews as list_overviews_direct
from infrastructure.db.models.base import Base
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.task.task import Task as TaskModel

load_models()


def _seed(session: Session, count: int) -> None:
    for index in range(count):
        session.add(
            TaskModel(
                title=f"Benchmark task {index}",
                description="Long description " * 50,
                task_type="task_translate_full_program",
                difficulty="medium",
                test_cases=[{"input": "x" * 200, "output": "y" * 200} for _ in range(5)],
                code_examples={
                    "patterns": ["loop_for"],
                    "python": "print('starter')\n" * 200,
                    "curriculum_showcase": {
                        "slug": f"slot_{index:03d}",
                        "collection_key": "loops",
                        "target_language": "python",
                        "task_format": "перевод",
                    },
                },
            )
        )
    session.commit()


def _measure(label: str, session: Session, fn) -> dict[str, float | int]:
    counter = {"count": 0}
    bind = session.get_bind()

    @event.listens_for(bind, "before_cursor_execute")
    def _count(conn, cursor, statement, parameters, context, executemany) -> None:
        counter["count"] += 1

    started = time.perf_counter()
    payload = fn()
    elapsed_ms = (time.perf_counter() - started) * 1000
    encoded = json.dumps(payload, ensure_ascii=False)
    event.remove(bind, "before_cursor_execute", _count)
    return {
        "label": label,
        "elapsed_ms": round(elapsed_ms, 2),
        "payload_bytes": len(encoded.encode("utf-8")),
        "sql_queries": counter["count"],
        "items": len(payload.get("tasks", payload if isinstance(payload, list) else [])),
    }


def main() -> int:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine, tables=[TaskModel.__table__])
    session = sessionmaker(bind=engine)()
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 500
    _seed(session, count)

    legacy = _measure(
        "legacy_full_list",
        session,
        lambda: {
            "tasks": [
                {
                    "id": t["id"],
                    "title": t["title"],
                    "description": t["description"],
                    "code_examples": t.get("code_examples"),
                    "test_cases": t.get("test_cases"),
                    "blocks": t.get("blocks", []),
                    "construction_hints": t.get("construction_hints", {}),
                }
                for t in list_tasks(session, allowed_task_ids=None)
            ]
        },
    )
    overview = _measure(
        "overview_light",
        session,
        lambda: list_overviews_direct(session, allowed_task_ids=None),
    )

    print(json.dumps({"count": count, "legacy": legacy, "overview": overview}, indent=2))
    session.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
