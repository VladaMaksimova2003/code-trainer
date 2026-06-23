#!/usr/bin/env python3
"""Print all Pascal showcase tasks with conditions (RU)."""
from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.display.showcase_display import sanitize_public_task_payload
from application.curriculum.pascal.showcase.pascal_showcase_registry import PASCAL_SHOWCASE_COLLECTIONS
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.models.task.task import Task as TaskModel
from infrastructure.db.session import SessionLocal

ACTION_RU = {
    "translate": "Перевод",
    "implement": "Написать программу",
    "debug": "Исправить код",
    "analyze": "Предсказать вывод",
    "assemble": "Собрать из блоков",
    "recognize": "Распознать",
}

DIFF_RU = {"easy": "лёгкая", "medium": "средняя", "hard": "сложная"}


def fmt_tests(tests: list[dict], expected_output: str | None) -> str:
    if tests:
        parts = []
        for i, t in enumerate(tests, 1):
            inp = str(t.get("inputs", "")).replace("\n", "\\n")
            out = str(t.get("output", t.get("expected", "")))
            parts.append(f"тест {i}: ввод «{inp}» → «{out}»")
        return "; ".join(parts)
    if expected_output:
        return f"ожидаемый вывод: «{expected_output}»"
    return "—"


def main() -> None:
    load_models()
    col_titles = {c.chapter_key: c.title_ru for c in PASCAL_SHOWCASE_COLLECTIONS}
    session = SessionLocal()
    rows = (
        session.query(TaskModel)
        .filter(TaskModel.is_delete.is_(False))
        .order_by(TaskModel.id.asc())
        .all()
    )
    by_col: dict[str, list[dict]] = {}
    for row in rows:
        ce = row.code_examples or {}
        showcase = ce.get("curriculum_showcase") or {}
        if not showcase.get("slug"):
            continue
        ck = str(showcase.get("collection_key") or "other")
        payload = sanitize_public_task_payload(
            {
                "id": row.id,
                "title": row.title,
                "description": row.description,
                "code_examples": ce,
                "test_cases": row.test_cases or [],
                "curriculum": {},
            }
        )
        by_col.setdefault(ck, []).append(
            {
                "id": row.id,
                "slot": showcase.get("slot_id"),
                "action": showcase.get("primary_action") or "?",
                "title": payload.get("title") or row.title,
                "desc": (row.description or "").strip(),
                "short": (showcase.get("short_instruction") or "").strip(),
                "diff": row.difficulty,
                "tests": fmt_tests(row.test_cases or [], showcase.get("expected_output")),
            }
        )
    session.close()

    total = 0
    for col in PASCAL_SHOWCASE_COLLECTIONS:
        items = by_col.get(col.chapter_key, [])
        if not items:
            continue
        print(f"## {col.title_ru} ({len(items)} задач)\n")
        for n, t in enumerate(items, 1):
            action = ACTION_RU.get(str(t["action"]), t["action"])
            diff = DIFF_RU.get(str(t["diff"]), t["diff"])
            print(f"**{n}. [{t['id']}] {t['title']}**")
            print(f"   Тип: {action} · {diff}")
            if t["short"] and t["short"] != t["desc"]:
                print(f"   Кратко: {t['short']}")
            print(f"   Условие: {t['desc']}")
            print(f"   Проверка: {t['tests']}")
            print()
        total += len(items)
        print()
    print(f"Всего: {total} задач")


if __name__ == "__main__":
    main()
