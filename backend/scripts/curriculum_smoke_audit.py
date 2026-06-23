#!/usr/bin/env python3
"""Smoke audit for Pascal v3.2, Python v1.2, C++ v1.2 curriculum."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from application.curriculum.collections.curriculum_collections_registry import list_curriculum_collections
from application.curriculum.collections.curriculum_language_catalog import list_home_languages
from application.curriculum.collections.curriculum_next_service import build_curriculum_collections_view
from application.curriculum.cpp.catalog.cpp_curriculum_v3_catalog import (
    all_v311_task_records as cpp_records,
    catalog_summary as cpp_summary,
    validate_v311_catalog as validate_cpp,
)
from application.curriculum.cpp.showcase.cpp_showcase_core import list_cpp_tasks_for_collection
from application.curriculum.cpp.showcase.cpp_v311_registry import (
    CPP_V311_SHOWCASE_COLLECTIONS,
    V311_COLLECTION_TARGETS as CPP_TARGETS,
)
from application.curriculum.mirror.universal_core_validation import validate_no_duplicate_pedagogical_slot_ids
from application.curriculum.pascal.catalog.pascal_curriculum_v3_catalog import (
    catalog_summary as pascal_summary,
    validate_v311_catalog as validate_pascal,
    V311_TOTAL_TASKS as PASCAL_TOTAL,
)
from application.curriculum.pascal.showcase.pascal_showcase_core import list_showcase_tasks_for_collection
from application.curriculum.pascal.showcase.pascal_v311_registry import (
    PASCAL_V311_SHOWCASE_COLLECTIONS,
    V311_COLLECTION_TARGETS as PASCAL_TARGETS,
)
from application.curriculum.python.catalog.python_curriculum_v3_catalog import (
    catalog_summary as python_summary,
    validate_v311_catalog as validate_python,
    V311_TOTAL_TASKS as PYTHON_TOTAL,
)
from application.curriculum.python.showcase.python_showcase_core import list_showcase_tasks_for_collection
from application.curriculum.python.showcase.python_v311_registry import (
    PYTHON_V311_SHOWCASE_COLLECTIONS,
    V311_COLLECTION_TARGETS as PYTHON_TARGETS,
)
from infrastructure.db.models.task.registry import load_models
from infrastructure.db.session import SessionLocal

ALLOWED_FORMATS = {
    "перевод_фрагмента",
    "перевод_программы",
    "исправление",
    "поиск_ошибки",
    "сборка_фрагмента",
    "сборка_программы",
    "выбор_фрагмента",
    "код_по_блок-схеме",
    "блок-схема_по_коду",
}
FORBIDDEN_FORMATS = {"сопоставление", "matching"}
FORBIDDEN_ACTIONS = {"analyze"}


def _audit_catalog(name: str, records_fn, validate_fn, summary_fn, registry, targets) -> dict:
    records = records_fn()
    summary = summary_fn()
    errors = validate_fn()
    formats = Counter(r.task_format for r in records)
    actions = Counter(r.primary_action for r in records)
    bad_fmt = [r.slot_id for r in records if r.task_format in FORBIDDEN_FORMATS]
    bad_act = [r.slot_id for r in records if r.primary_action in FORBIDDEN_ACTIONS]
    unknown_fmt = [r.slot_id for r in records if r.task_format not in ALLOWED_FORMATS]
    chapters = len(registry)
    target_sum = sum(targets.values())
    return {
        "name": name,
        "catalog_tasks": len(records),
        "expected_tasks": target_sum,
        "chapters_registry": chapters,
        "chapters_summary": summary.get("chapters"),
        "validate_errors": errors,
        "forbidden_format_slots": bad_fmt,
        "forbidden_action_slots": bad_act,
        "unknown_format_slots": unknown_fmt[:5],
        "unknown_format_count": len(unknown_fmt),
        "formats": dict(formats),
        "actions": dict(actions),
    }


def _audit_db_collections(session, language: str, registry, targets, list_fn, *, curriculum_version: str | None = None) -> list[dict]:
    rows: list[dict] = []
    for col in registry:
        if curriculum_version is not None:
            tasks = list_fn(session, col.chapter_key, curriculum_version=curriculum_version)
        else:
            tasks = list_fn(session, col.chapter_key)
        slugs = [str(t.get("slug") or "") for t in tasks]
        dup_slugs = [s for s, c in Counter(slugs).items() if c > 1 and s]
        dup_ids = [tid for tid, c in Counter(t["task_id"] for t in tasks).items() if c > 1]
        rows.append(
            {
                "chapter": col.chapter_key,
                "expected": targets.get(col.chapter_key, 0),
                "db_count": len(tasks),
                "duplicate_slugs": dup_slugs,
                "duplicate_task_ids": dup_ids,
            }
        )
    return rows


def main() -> int:
    load_models()
    session = SessionLocal()
    issues: list[str] = []

    catalog_reports = [
        _audit_catalog(
            "pascal",
            lambda: __import__(
                "application.curriculum.pascal.catalog.pascal_curriculum_v3_catalog",
                fromlist=["all_v311_task_records"],
            ).all_v311_task_records(),
            validate_pascal,
            pascal_summary,
            PASCAL_V311_SHOWCASE_COLLECTIONS,
            PASCAL_TARGETS,
        ),
        _audit_catalog("python", lambda: __import__(
            "application.curriculum.python.catalog.python_curriculum_v3_catalog",
            fromlist=["all_v311_task_records"],
        ).all_v311_task_records(), validate_python, python_summary, PYTHON_V311_SHOWCASE_COLLECTIONS, PYTHON_TARGETS),
        _audit_catalog("cpp", cpp_records, validate_cpp, cpp_summary, CPP_V311_SHOWCASE_COLLECTIONS, CPP_TARGETS),
    ]

    dup_errors = validate_no_duplicate_pedagogical_slot_ids(session)
    collections_view = build_curriculum_collections_view(session, None)
    home_langs = {item.language: item for item in list_home_languages()}
    registry_langs = Counter(c.language for c in list_curriculum_collections())

    db_pascal = _audit_db_collections(
        session, "pascal", PASCAL_V311_SHOWCASE_COLLECTIONS, PASCAL_TARGETS,
        list_showcase_tasks_for_collection, curriculum_version="3.1.1",
    )
    db_python = _audit_db_collections(
        session, "python", PYTHON_V311_SHOWCASE_COLLECTIONS, PYTHON_TARGETS,
        list_showcase_tasks_for_collection, curriculum_version="1.0",
    )
    db_cpp = _audit_db_collections(session, "cpp", CPP_V311_SHOWCASE_COLLECTIONS, CPP_TARGETS, list_cpp_tasks_for_collection)

    for rep in catalog_reports:
        if rep["catalog_tasks"] != rep["expected_tasks"]:
            issues.append(f"{rep['name']}: catalog count mismatch")
        if rep["chapters_registry"] != rep["chapters_summary"]:
            issues.append(f"{rep['name']}: chapter count mismatch")
        if rep["validate_errors"]:
            issues.append(f"{rep['name']}: catalog validation failed")
        if rep["forbidden_format_slots"] or rep["forbidden_action_slots"]:
            issues.append(f"{rep['name']}: forbidden format/action in catalog")

    for lang_block in collections_view.get("languages", []):
        lang = lang_block.get("language")
        if lang in {"csharp", "java"}:
            continue
        if lang in home_langs and not lang_block.get("available"):
            issues.append(f"UI language {lang} not available in collections view")
        if lang in {"pascal", "python", "cpp"}:
            expected_ch = registry_langs[lang]
            actual_ch = len(lang_block.get("collections") or [])
            if actual_ch != expected_ch:
                issues.append(f"{lang}: collections view chapters {actual_ch} != registry {expected_ch}")

    for block, lang in ((db_pascal, "pascal"), (db_python, "python"), (db_cpp, "cpp")):
        for row in block:
            if row["db_count"] != row["expected"]:
                issues.append(
                    f"{lang}/{row['chapter']}: db tasks {row['db_count']} != expected {row['expected']}"
                )
            if row["duplicate_slugs"] or row["duplicate_task_ids"]:
                issues.append(f"{lang}/{row['chapter']}: duplicates in DB listing")

    report = {
        "catalog": catalog_reports,
        "constants": {
            "pascal_total_constant": PASCAL_TOTAL,
            "python_total_constant": PYTHON_TOTAL,
        },
        "duplicate_pedagogical_slot_ids": dup_errors,
        "home_languages": [
            {"language": k, "label": v.language_label, "available_flag": True}
            for k, v in home_langs.items()
        ],
        "registry_collection_counts": dict(registry_langs),
        "collections_view_counts": {
            block["language"]: len(block.get("collections") or [])
            for block in collections_view.get("languages", [])
        },
        "db_mismatches": {
            "pascal": [r for r in db_pascal if r["db_count"] != r["expected"]],
            "python": [r for r in db_python if r["db_count"] != r["expected"]],
            "cpp": [r for r in db_cpp if r["db_count"] != r["expected"]],
        },
        "issues": issues,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    session.close()
    return 1 if issues or dup_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
