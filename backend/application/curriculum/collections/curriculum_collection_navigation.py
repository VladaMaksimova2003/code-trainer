"""Student-facing navigation within a curriculum showcase collection (Pascal, Python, or C++)."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from application.curriculum.collections.curriculum_collections_registry import get_collection_by_id
from application.curriculum.pascal.showcase.pascal_showcase_all_specs import all_pascal_showcase_specs
from application.curriculum.pascal.showcase.pascal_showcase_next import order_collection_showcase_tasks
from application.curriculum.pascal.showcase.pascal_showcase_registry import PASCAL_SHOWCASE_COLLECTIONS, collection_by_key
from application.curriculum.pascal.showcase.pascal_v311_registry import (
    PASCAL_V311_SHOWCASE_COLLECTIONS,
    v311_collection_by_key as pascal_v311_collection_by_key,
)
from application.curriculum.pascal.showcase.pascal_v311_showcase_all_specs import (
    all_pascal_v311_showcase_specs,
    pascal_v311_showcase_specs_for_collection,
)
from application.curriculum.python.showcase.python_v311_registry import (
    PYTHON_V311_SHOWCASE_COLLECTIONS,
    v311_collection_by_key as python_v311_collection_by_key,
)
from application.curriculum.python.showcase.python_v311_showcase_all_specs import (
    python_v311_showcase_specs_for_collection,
)
from application.curriculum.python.showcase.python_showcase_next import order_collection_showcase_tasks as order_python_tasks
from application.curriculum.cpp.showcase.cpp_v311_registry import (
    CPP_V311_SHOWCASE_COLLECTIONS,
    v311_collection_by_key as cpp_v311_collection_by_key,
)
from application.curriculum.cpp.showcase.cpp_v311_showcase_all_specs import (
    cpp_v311_showcase_specs_for_collection,
)
from application.curriculum.cpp.showcase.cpp_showcase_next import order_collection_showcase_tasks as order_cpp_tasks
from application.curriculum.csharp.showcase.csharp_v311_registry import (
    CSHARP_V311_SHOWCASE_COLLECTIONS,
    v311_collection_by_key as csharp_v311_collection_by_key,
)
from application.curriculum.csharp.showcase.csharp_v311_showcase_all_specs import (
    csharp_v311_showcase_specs_for_collection,
)
from application.curriculum.csharp.showcase.csharp_showcase_next import (
    order_collection_showcase_tasks as order_csharp_tasks,
)
from application.curriculum.java.showcase.java_v311_registry import (
    JAVA_V311_SHOWCASE_COLLECTIONS,
    v311_collection_by_key as java_v311_collection_by_key,
)
from application.curriculum.java.showcase.java_v311_showcase_all_specs import (
    java_v311_showcase_specs_for_collection,
)
from application.curriculum.java.showcase.java_showcase_next import order_collection_showcase_tasks as order_java_tasks
from infrastructure.db.models.task.task import Task as TaskModel


def _ordered_pascal_task_ids(session: Session, chapter_key: str) -> list[int]:
    v311_col = pascal_v311_collection_by_key(chapter_key)
    if v311_col is not None:
        specs = pascal_v311_showcase_specs_for_collection(chapter_key)
        ordered = order_collection_showcase_tasks(session, chapter_key, specs)
        if ordered:
            return [int(row["task_id"]) for row in ordered]
    v2_specs = all_pascal_showcase_specs().get(chapter_key, ())
    ordered = order_collection_showcase_tasks(session, chapter_key, v2_specs)
    if ordered:
        return [int(row["task_id"]) for row in ordered]
    from application.curriculum.pascal.legacy.loops.loops_showcase_seeder import list_showcase_tasks as _list_loops
    from application.curriculum.pascal.legacy.conditions.conditions_showcase_seeder import list_showcase_tasks as _list_cond

    _LEGACY_LISTS = {"loops": _list_loops, "conditions": _list_cond}
    if chapter_key in _LEGACY_LISTS:
        rows = _LEGACY_LISTS[chapter_key](session)
        return [int(r["task_id"]) for r in rows]
    return []


def _ordered_python_task_ids(session: Session, chapter_key: str) -> list[int]:
    v311_col = python_v311_collection_by_key(chapter_key)
    if v311_col is None:
        return []
    specs = python_v311_showcase_specs_for_collection(chapter_key)
    ordered = order_python_tasks(session, chapter_key, specs)
    if ordered:
        return [int(row["task_id"]) for row in ordered]
    return []


def _ordered_cpp_task_ids(session: Session, chapter_key: str) -> list[int]:
    v311_col = cpp_v311_collection_by_key(chapter_key)
    if v311_col is None:
        return []
    specs = cpp_v311_showcase_specs_for_collection(chapter_key)
    ordered = order_cpp_tasks(session, chapter_key, specs)
    if ordered:
        return [int(row["task_id"]) for row in ordered]
    return []


def _ordered_java_task_ids(session: Session, chapter_key: str) -> list[int]:
    v311_col = java_v311_collection_by_key(chapter_key)
    if v311_col is None:
        return []
    specs = java_v311_showcase_specs_for_collection(chapter_key)
    ordered = order_java_tasks(session, chapter_key, specs)
    if ordered:
        return [int(row["task_id"]) for row in ordered]
    return []


def _ordered_csharp_task_ids(session: Session, chapter_key: str) -> list[int]:
    v311_col = csharp_v311_collection_by_key(chapter_key)
    if v311_col is None:
        return []
    specs = csharp_v311_showcase_specs_for_collection(chapter_key)
    ordered = order_csharp_tasks(session, chapter_key, specs)
    if ordered:
        return [int(row["task_id"]) for row in ordered]
    return []


def _get_collection(language: str, chapter_key: str):
    lang = language.strip().lower()
    if lang == "python":
        return python_v311_collection_by_key(chapter_key)
    if lang == "cpp":
        return cpp_v311_collection_by_key(chapter_key)
    if lang == "java":
        return java_v311_collection_by_key(chapter_key)
    if lang == "csharp":
        return csharp_v311_collection_by_key(chapter_key)
    v311 = pascal_v311_collection_by_key(chapter_key)
    if v311 is not None:
        return v311
    return collection_by_key(chapter_key)


def _all_chapter_keys(language: str) -> list[str]:
    lang = language.strip().lower()
    if lang == "python":
        return [c.chapter_key for c in PYTHON_V311_SHOWCASE_COLLECTIONS]
    if lang == "cpp":
        return [c.chapter_key for c in CPP_V311_SHOWCASE_COLLECTIONS]
    if lang == "java":
        return [c.chapter_key for c in JAVA_V311_SHOWCASE_COLLECTIONS]
    if lang == "csharp":
        return [c.chapter_key for c in CSHARP_V311_SHOWCASE_COLLECTIONS]
    return [c.chapter_key for c in PASCAL_V311_SHOWCASE_COLLECTIONS]


def _ordered_task_ids(session: Session, *, language: str, chapter_key: str) -> list[int]:
    lang = language.strip().lower()
    if lang == "python":
        return _ordered_python_task_ids(session, chapter_key)
    if lang == "cpp":
        return _ordered_cpp_task_ids(session, chapter_key)
    if lang == "java":
        return _ordered_java_task_ids(session, chapter_key)
    if lang == "csharp":
        return _ordered_csharp_task_ids(session, chapter_key)
    return _ordered_pascal_task_ids(session, chapter_key)


def build_collection_navigation(
    session: Session,
    *,
    language: str,
    chapter_key: str,
    task_id: int,
) -> dict[str, Any] | None:
    col = _get_collection(language, chapter_key)
    if col is None:
        return None

    task_ids = _ordered_task_ids(session, language=language, chapter_key=chapter_key)
    if task_id not in task_ids:
        return None

    index = task_ids.index(task_id)
    is_last_in_collection = index >= len(task_ids) - 1
    next_task_id = task_ids[index + 1] if not is_last_in_collection else None
    next_collection_id: str | None = None
    next_collection_title_ru: str | None = None
    prev_collection_id: str | None = None
    course_completed = False

    prev_task_id = task_ids[index - 1] if index > 0 else None
    if index == 0:
        col_keys = _all_chapter_keys(language)
        try:
            col_idx = col_keys.index(chapter_key)
        except ValueError:
            col_idx = -1
        if col_idx > 0:
            prev_chapter_key = col_keys[col_idx - 1]
            prev_ids = _ordered_task_ids(session, language=language, chapter_key=prev_chapter_key)
            if prev_ids:
                prev_task_id = prev_ids[-1]
                prev_col = _get_collection(language, prev_chapter_key)
                if prev_col is not None:
                    prev_collection_id = prev_col.collection_id

    if is_last_in_collection:
        col_keys = _all_chapter_keys(language)
        try:
            col_idx = col_keys.index(chapter_key)
        except ValueError:
            col_idx = -1
        if col_idx >= 0 and col_idx < len(col_keys) - 1:
            next_chapter_key = col_keys[col_idx + 1]
            next_col = _get_collection(language, next_chapter_key)
            next_ids = _ordered_task_ids(session, language=language, chapter_key=next_chapter_key)
            if next_ids:
                next_task_id = next_ids[0]
                if next_col is not None:
                    next_collection_id = next_col.collection_id
                    next_collection_title_ru = next_col.title_ru
        elif col_idx == len(col_keys) - 1:
            course_completed = True

    return {
        "language": language.strip().lower(),
        "collection_id": col.collection_id,
        "collection_title_ru": col.title_ru,
        "return_path": col.route_path,
        "task_index": index + 1,
        "total_tasks": len(task_ids),
        "task_ids": task_ids,
        "prev_task_id": prev_task_id,
        "prev_collection_id": prev_collection_id,
        "next_task_id": next_task_id,
        "next_collection_id": next_collection_id,
        "next_collection_title_ru": next_collection_title_ru,
        "course_completed": course_completed,
    }


def build_collection_navigation_by_collection_id(
    session: Session,
    *,
    collection_id: str,
    task_id: int,
) -> dict[str, Any] | None:
    from application.curriculum.showcase.showcase_task_index import run_with_showcase_task_index

    definition = get_collection_by_id(collection_id)
    if definition is None:
        return None

    return run_with_showcase_task_index(
        session,
        lambda: build_collection_navigation(
            session,
            language=definition.language,
            chapter_key=definition.chapter_key,
            task_id=task_id,
        ),
    )


def _language_from_showcase(showcase: dict[str, Any]) -> str | None:
    group = str(showcase.get("group") or "")
    if group.startswith("python_curriculum_v311_"):
        return "python"
    if group.startswith("pascal_curriculum_v311_"):
        return "pascal"
    if group.startswith("cpp_curriculum_v311_"):
        return "cpp"
    if group.startswith("csharp_curriculum_v311_"):
        return "csharp"
    if group.startswith("java_curriculum_v311_"):
        return "java"
    return None


def build_collection_navigation_for_task(
    session: Session,
    task_id: int,
    *,
    learning_language: str | None = None,
) -> dict[str, Any] | None:
    return _build_collection_navigation_for_task(
        session,
        task_id,
        learning_language=learning_language,
    )


def _build_collection_navigation_for_task(
    session: Session,
    task_id: int,
    *,
    learning_language: str | None = None,
) -> dict[str, Any] | None:
    task = session.get(TaskModel, task_id)
    if task is None or task.is_delete:
        return None

    examples = dict(task.code_examples or {})
    showcase = dict(examples.get("curriculum_showcase") or {})
    from application.curriculum.mirror.pedagogical_task_store import language_track, resolved_showcase

    if learning_language:
        showcase = resolved_showcase(showcase, learning_language)

    collection_key = showcase.get("collection_key")
    language = _language_from_showcase(showcase) or (
        learning_language.strip().lower() if learning_language else None
    )
    if collection_key and language:
        return build_collection_navigation(
            session,
            language=language,
            chapter_key=str(collection_key),
            task_id=task_id,
        )

    preferred = learning_language.strip().lower() if learning_language else None
    if preferred in {"pascal", "python", "cpp", "csharp", "java"}:
        others = [lang for lang in ("python", "pascal", "cpp", "csharp", "java") if lang != preferred]
        search_order = [preferred, *others]
    else:
        search_order = ["python", "pascal", "cpp", "csharp", "java"]
    for lang in search_order:
        track = language_track(showcase, lang)
        track_col = str(track.get("collection_key") or "")
        if track_col:
            navigation = build_collection_navigation(
                session,
                language=lang,
                chapter_key=track_col,
                task_id=task_id,
            )
            if navigation is not None:
                return navigation

    return None
