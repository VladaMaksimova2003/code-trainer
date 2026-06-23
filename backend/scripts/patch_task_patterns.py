#!/usr/bin/env python3
"""Backfill code_examples.patterns for showcase tasks missing skill tags."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import select

from application.tasks.services.task_patterns import apply_patterns_and_tests
from infrastructure.db.models.task import Task as TaskModel
from infrastructure.db.session import SessionLocal

PATTERNS_BY_TITLE: dict[str, list[str]] = {
    "Суммирование элементов": ["for_loop", "assign"],
    "Знак числа": ["if_statement", "io"],
    "Вложенные циклы": ["nested_loops", "for_loop", "io"],
    "Квадрат числа": ["assign", "io", "binary_expression"],
    "Минимум из двух": ["io", "assign"],
    "Таблица умножения": ["for_loop", "io"],
    "Удвоить число": ["assign", "io"],
    "Чётное или нечётное": ["if_statement", "io"],
    "Сумма от 1 до n": ["for_loop", "assign", "io"],
}


def main() -> None:
    from infrastructure.db.models.task.registry import load_models
    from sqlalchemy.orm import configure_mappers

    load_models()
    configure_mappers()

    session = SessionLocal()
    updated = 0
    try:
        rows = session.execute(select(TaskModel)).scalars().all()
        for row in rows:
            patterns = PATTERNS_BY_TITLE.get(row.title or "")
            if not patterns:
                continue
            examples = dict(row.code_examples or {})
            if examples.get("patterns"):
                continue
            apply_patterns_and_tests(row, patterns=patterns, test_cases=None)
            updated += 1
            print(f"  + {row.id}: {row.title}")
        session.commit()
        print(f"Patched patterns on {updated} task(s).")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
