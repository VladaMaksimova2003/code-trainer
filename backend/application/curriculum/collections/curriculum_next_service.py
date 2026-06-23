"""Linear next-task selection for curriculum showcase collections."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from sqlalchemy.orm import Session

from application.curriculum.showcase.showcase_task_index import (
    ShowcaseTaskIndex,
    activate_showcase_task_index,
    get_showcase_task_index,
    reset_showcase_task_index,
)
from application.curriculum.pascal.legacy.conditions.conditions_showcase_data import (
    TITLE_PREFIX as CONDITIONS_TITLE_PREFIX,
    conditions_showcase_specs,
)
from application.curriculum.pascal.legacy.conditions.conditions_showcase_seeder import list_showcase_tasks as list_conditions_showcase_tasks
from application.curriculum.collections.curriculum_language_catalog import list_home_languages
from application.curriculum.collections.curriculum_collections_registry import (
    PASCAL_CONDITIONS_COLLECTION_ID,
    PASCAL_LOOPS_COLLECTION_ID,
    CurriculumCollectionDefinition,
    get_collection_by_id,
    list_curriculum_collections,
)
from application.curriculum.showcase.showcase_task_index import (
    ShowcaseTaskIndex,
    activate_showcase_task_index,
    get_showcase_task_index,
    reset_showcase_task_index,
)
from application.curriculum.display.chapter_task_display_order import (
    SHOWCASE_PEDAGOGICAL_ACTION_ORDER,
    pedagogical_action_sort_key,
    showcase_row_sort_key,
)
from application.curriculum.core.curriculum_service import CurriculumService
from application.curriculum.pascal.legacy.loops.loops_showcase_data import TITLE_PREFIX as LOOPS_TITLE_PREFIX, loops_showcase_specs
from application.curriculum.pascal.legacy.loops.loops_showcase_seeder import list_showcase_tasks as list_loops_showcase_tasks
from application.curriculum.progress.student_curriculum_progress_service import (
    PROGRESS_STATUS_NOT_STARTED,
    PROGRESS_STATUS_PASSED,
    StudentCurriculumProgressService,
    activate_batch_progress_cache,
    reset_batch_progress_cache,
)

# Next-task route: blocks → fix → write (see chapter_task_display_order.py).
NEXT_TASK_ACTION_ORDER = SHOWCASE_PEDAGOGICAL_ACTION_ORDER

_LOOPS_SPEC_SEED_INDEX = {spec.slug: index for index, spec in enumerate(loops_showcase_specs())}
_CONDITIONS_SPEC_SEED_INDEX = {spec.slug: index for index, spec in enumerate(conditions_showcase_specs())}


def _display_title(title: str, *, title_prefix: str) -> str:
    if title.startswith(title_prefix):
        return title[len(title_prefix) :].strip()
    return title.strip()


def _action_sort_key(action: str | None) -> int:
    return pedagogical_action_sort_key(action)


def order_showcase_tasks(
    session: Session,
    *,
    language: str = "pascal",
    learning_concept_id: str = "loops",
    list_fn: Callable[[Session], list[dict[str, Any]]] | None = None,
    spec_seed_index: dict[str, int] | None = None,
) -> list[dict[str, Any]]:
    if list_fn is None:
        list_fn = list_loops_showcase_tasks
    if spec_seed_index is None:
        spec_seed_index = _LOOPS_SPEC_SEED_INDEX

    rows = list_fn(session)
    chapter = CurriculumService(language).get_learning_concept_detail(language, learning_concept_id)
    study_order_tc = list(chapter["study_order_tc"])
    tc_index = {tc_id: index for index, tc_id in enumerate(study_order_tc)}

    def sort_key(row: dict[str, Any]) -> tuple[int, int, int, int, int]:
        return showcase_row_sort_key(
            row,
            tc_index=tc_index,
            spec_index=spec_seed_index,
            action_sort_key=_action_sort_key,
        )

    return sorted(rows, key=sort_key)


def order_loops_showcase_tasks(session: Session, *, language: str = "pascal") -> list[dict[str, Any]]:
    return order_showcase_tasks(
        session,
        language=language,
        learning_concept_id="loops",
        list_fn=list_loops_showcase_tasks,
        spec_seed_index=_LOOPS_SPEC_SEED_INDEX,
    )


def order_conditions_showcase_tasks(session: Session, *, language: str = "pascal") -> list[dict[str, Any]]:
    return order_showcase_tasks(
        session,
        language=language,
        learning_concept_id="conditions",
        list_fn=list_conditions_showcase_tasks,
        spec_seed_index=_CONDITIONS_SPEC_SEED_INDEX,
    )


def _progress_map(
    session: Session,
    user_id: int | None,
    task_ids: list[int],
    *,
    learning_concept_id: str,
) -> dict[int, str]:
    if user_id is None or not task_ids:
        return {}
    progress = StudentCurriculumProgressService(session).get_progress_for_learning_concept(
        user_id,
        "pascal",
        learning_concept_id,
        task_ids=task_ids,
    )
    return {
        int(tid): item["progress_status"]
        for tid, item in progress["by_task_id"].items()
    }


def _progress_summary(total: int, progress_by_task: dict[int, str], task_ids: list[int]) -> dict[str, Any]:
    passed = sum(
        1 for tid in task_ids if progress_by_task.get(tid) == PROGRESS_STATUS_PASSED
    )
    percent = round(100.0 * passed / total, 1) if total else 0.0
    return {
        "total_tasks": total,
        "passed_tasks": passed,
        "progress_percent": percent,
    }


def _task_payload(row: dict[str, Any], progress_status: str, *, title_prefix: str) -> dict[str, Any]:
    return {
        "task_id": row["task_id"],
        "slug": row.get("slug"),
        "title": _display_title(str(row.get("title") or ""), title_prefix=title_prefix),
        "task_type": row.get("task_type"),
        "technical_concept_id": row.get("technical_concept_id"),
        "action": row.get("action"),
        "progress_status": progress_status,
    }


def _global_button_label(*, passed_tasks: int, total_tasks: int, completed: bool) -> str:
    if passed_tasks <= 0:
        return "Начать обучение"
    if completed:
        return "Повторить обучение"
    return "Продолжить обучение"


def _collection_button_label(*, passed_tasks: int, total_tasks: int, completed: bool) -> str:
    if passed_tasks <= 0:
        return "Начать сборник"
    if completed:
        return "Повторить сборник"
    return "Продолжить сборник"


def _collection_card_button_label(*, passed_tasks: int, completed: bool) -> str:
    if passed_tasks <= 0:
        return "Начать"
    if completed:
        return "Повторить"
    return "Продолжить"


def resolve_next_in_ordered_tasks(
    ordered_tasks: list[dict[str, Any]],
    progress_by_task: dict[int, str],
    *,
    title_prefix: str,
) -> tuple[dict[str, Any] | None, bool]:
    if not ordered_tasks:
        return None, False

    for row in ordered_tasks:
        task_id = int(row["task_id"])
        status = progress_by_task.get(task_id, PROGRESS_STATUS_NOT_STARTED)
        if status != PROGRESS_STATUS_PASSED:
            return _task_payload(row, status, title_prefix=title_prefix), False

    first = ordered_tasks[0]
    first_id = int(first["task_id"])
    return (
        _task_payload(first, progress_by_task.get(first_id, PROGRESS_STATUS_PASSED), title_prefix=title_prefix),
        True,
    )


def build_pascal_conditions_showcase_next(session: Session, user_id: int | None) -> dict[str, Any]:
    from application.curriculum.pascal.showcase.pascal_showcase_next import build_pascal_showcase_collection_next

    return build_pascal_showcase_collection_next(session, "conditions", user_id)


def build_pascal_loops_showcase_next(session: Session, user_id: int | None) -> dict[str, Any]:
    from application.curriculum.pascal.showcase.pascal_showcase_next import build_pascal_showcase_collection_next

    return build_pascal_showcase_collection_next(session, "loops", user_id)


def _curriculum_version_for_language(language: str) -> str:
    return "3.1.1" if language.strip().lower() == "pascal" else "1.0"


def _spec_count_for_collection(language: str, chapter_key: str) -> int:
    lang = language.strip().lower()
    if lang == "pascal":
        from application.curriculum.pascal.showcase.pascal_v311_registry import V311_COLLECTION_TARGETS

        return int(V311_COLLECTION_TARGETS.get(chapter_key, 0))
    if lang == "python":
        from application.curriculum.python.showcase.python_v311_registry import V311_COLLECTION_TARGETS

        return int(V311_COLLECTION_TARGETS.get(chapter_key, 0))
    if lang == "cpp":
        from application.curriculum.cpp.showcase.cpp_v311_registry import V311_COLLECTION_TARGETS

        return int(V311_COLLECTION_TARGETS.get(chapter_key, 0))
    if lang == "csharp":
        from application.curriculum.csharp.showcase.csharp_v311_registry import V311_COLLECTION_TARGETS

        return int(V311_COLLECTION_TARGETS.get(chapter_key, 0))
    if lang == "java":
        from application.curriculum.java.showcase.java_v311_registry import V311_COLLECTION_TARGETS

        return int(V311_COLLECTION_TARGETS.get(chapter_key, 0))
    return 0


def _list_tasks_for_collection_summary(
    session: Session,
    definition: CurriculumCollectionDefinition,
    *,
    index: ShowcaseTaskIndex,
    allow_db_fallback: bool = True,
) -> list[dict[str, Any]]:
    version = _curriculum_version_for_language(definition.language)
    rows = index.list_for_collection(
        definition.language,
        definition.chapter_key,
        curriculum_version=version,
    ) or []
    if rows:
        return rows
    if not allow_db_fallback:
        return []

    lang = definition.language.strip().lower()
    chapter_key = definition.chapter_key
    if lang == "csharp":
        from application.curriculum.csharp.showcase.csharp_showcase_core import list_csharp_tasks_for_collection

        return list_csharp_tasks_for_collection(session, chapter_key)
    if lang == "java":
        from application.curriculum.java.showcase.java_showcase_core import list_java_tasks_for_collection

        return list_java_tasks_for_collection(session, chapter_key)
    if lang == "cpp":
        from application.curriculum.cpp.showcase.cpp_showcase_core import list_cpp_tasks_for_collection

        return list_cpp_tasks_for_collection(session, chapter_key)
    if lang == "python":
        from application.curriculum.python.showcase.python_showcase_core import list_showcase_tasks_for_collection

        return list_showcase_tasks_for_collection(
            session,
            chapter_key,
            curriculum_version=version,
        )
    return []


def build_collection_summary_light(
    session: Session,
    definition: CurriculumCollectionDefinition,
    user_id: int | None,
    *,
    index: ShowcaseTaskIndex,
    meta_ctx: "ChapterMetaContext | None" = None,
) -> dict[str, Any]:
    from application.curriculum.chapters.curriculum_chapter_meta_service import (
        ChapterMetaContext,
        resolve_chapter_display,
    )

    version = _curriculum_version_for_language(definition.language)
    rows = _list_tasks_for_collection_summary(
        session,
        definition,
        index=index,
        allow_db_fallback=False,
    )
    task_ids = [int(row["task_id"]) for row in rows if row.get("task_id")]
    spec_total = _spec_count_for_collection(definition.language, definition.chapter_key)
    total = len(task_ids)

    progress_by_task: dict[int, str] = {}
    if user_id is not None and task_ids:
        progress = StudentCurriculumProgressService(session).get_progress_for_learning_concept(
            user_id,
            definition.language,
            definition.learning_concept_id,
            task_ids=task_ids,
        )
        progress_by_task = {
            int(tid): item["progress_status"]
            for tid, item in progress["by_task_id"].items()
        }

    if spec_total > 0 and total > spec_total:
        total = spec_total
    progress = _progress_summary(total, progress_by_task, task_ids)
    if spec_total > 0:
        progress = {**progress, "catalog_tasks": spec_total}
        if total > 0:
            progress["total_tasks"] = min(total, spec_total)
    completed = total > 0 and progress["passed_tasks"] >= total
    title_ru, description_ru = resolve_chapter_display(
        session,
        definition.language,
        definition.chapter_key,
        default_title=definition.title_ru,
        default_description=definition.description_ru,
        meta_ctx=meta_ctx,
    )
    return {
        "collection_id": definition.collection_id,
        "language": definition.language,
        "chapter_key": definition.chapter_key,
        "learning_concept_id": definition.learning_concept_id,
        "title_ru": title_ru,
        "description_ru": description_ru,
        "route_path": definition.route_path,
        "progress": progress,
        "completed": completed,
        "button_label": _collection_card_button_label(
            passed_tasks=progress["passed_tasks"],
            completed=completed,
        ),
        "next_task": None,
    }


def build_collection_summary(
    session: Session,
    definition: CurriculumCollectionDefinition,
    user_id: int | None,
    *,
    meta_ctx: "ChapterMetaContext | None" = None,
) -> dict[str, Any]:
    from application.curriculum.chapters.curriculum_chapter_meta_service import (
        ChapterMetaContext,
        resolve_chapter_display,
    )

    payload = definition.build_next(session, user_id)
    progress = payload["progress"]
    completed = bool(payload["completed"])
    title_ru, description_ru = resolve_chapter_display(
        session,
        definition.language,
        definition.chapter_key,
        default_title=definition.title_ru,
        default_description=definition.description_ru,
        meta_ctx=meta_ctx,
    )
    return {
        "collection_id": definition.collection_id,
        "language": definition.language,
        "chapter_key": definition.chapter_key,
        "learning_concept_id": definition.learning_concept_id,
        "title_ru": title_ru,
        "description_ru": description_ru,
        "route_path": definition.route_path,
        "progress": progress,
        "completed": completed,
        "button_label": _collection_card_button_label(
            passed_tasks=progress["passed_tasks"],
            completed=completed,
        ),
        "next_task": payload["next_task"],
    }


def _aggregate_progress(collections: list[dict[str, Any]]) -> dict[str, Any]:
    from application.curriculum.showcase.showcase_language_progress import (
        display_collection_total,
        effective_collection_total,
    )

    total = sum(effective_collection_total(item.get("progress") or {}) for item in collections)
    catalog_total = sum(display_collection_total(item.get("progress") or {}) for item in collections)
    passed = sum(item["progress"]["passed_tasks"] for item in collections)
    percent = round(100.0 * passed / total, 1) if total else 0.0
    result: dict[str, Any] = {
        "total_tasks": total,
        "passed_tasks": passed,
        "progress_percent": percent,
    }
    if catalog_total > 0:
        result["catalog_tasks"] = catalog_total
    return result


def _collection_ref_from_summary(summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "collection_id": summary["collection_id"],
        "language": summary["language"],
        "chapter_key": summary["chapter_key"],
        "learning_concept_id": summary["learning_concept_id"],
        "title_ru": summary["title_ru"],
        "route_path": summary["route_path"],
    }


def _sort_collection_summaries(
    session: Session,
    summaries: list[dict[str, Any]],
    *,
    language: str | None = None,
    meta_ctx: "ChapterMetaContext | None" = None,
) -> list[dict[str, Any]]:
    from application.curriculum.chapters.curriculum_chapter_meta_service import (
        ChapterMetaContext,
        list_chapters,
    )

    order_by_key = {
        str(item.chapter_key): int(item.sort_order)
        for item in list_chapters(session, language=language, meta_ctx=meta_ctx)
    }

    def sort_key(item: dict[str, Any]) -> tuple[int, str]:
        chapter_key = str(item.get("chapter_key") or "")
        return (
            order_by_key.get(chapter_key, 99999),
            str(item.get("title_ru") or chapter_key).lower(),
        )

    return sorted(summaries, key=sort_key)


def _append_custom_chapter_summaries(
    session: Session,
    summaries: list[dict[str, Any]],
    *,
    language: str | None = None,
    meta_ctx: "ChapterMetaContext | None" = None,
) -> list[dict[str, Any]]:
    from application.curriculum.chapters.curriculum_chapter_meta_service import (
        ChapterMetaContext,
        list_chapters,
    )

    existing = {str(item["chapter_key"]) for item in summaries}
    result = list(summaries)
    for chapter in list_chapters(session, language=language, meta_ctx=meta_ctx):
        if not chapter.is_custom or chapter.chapter_key in existing:
            continue
        total = chapter.task_count
        progress = {
            "total_tasks": total,
            "passed_tasks": 0,
            "progress_percent": 0.0,
        }
        result.append(
            {
                "collection_id": f"{chapter.language}_{chapter.chapter_key}_custom",
                "language": chapter.language,
                "chapter_key": chapter.chapter_key,
                "learning_concept_id": chapter.chapter_key,
                "title_ru": chapter.title,
                "description_ru": chapter.description,
                "route_path": f"/learn/{chapter.language}/{chapter.chapter_key}",
                "progress": progress,
                "completed": False,
                "button_label": _collection_card_button_label(passed_tasks=0, completed=False),
                "next_task": None,
            }
        )
    return _sort_collection_summaries(session, result, language=language, meta_ctx=meta_ctx)


def _build_all_collection_summaries(
    session: Session,
    user_id: int | None,
    *,
    language: str | None = None,
) -> list[dict[str, Any]]:
    from application.curriculum.chapters.curriculum_chapter_meta_service import load_chapter_meta_context

    definitions = list_curriculum_collections(language)
    token = activate_showcase_task_index(session)
    batch_token = activate_batch_progress_cache(session, user_id)
    try:
        index = get_showcase_task_index()
        meta_ctx = load_chapter_meta_context(
            session,
            language=language,
            task_counts_by_chapter=index.chapter_task_counts() if index is not None else None,
        )
        return [
            build_collection_summary(session, definition, user_id, meta_ctx=meta_ctx)
            for definition in definitions
        ]
    finally:
        reset_batch_progress_cache(batch_token)
        reset_showcase_task_index(token)


def _build_all_collection_summaries_light(
    session: Session,
    user_id: int | None,
    *,
    language: str | None = None,
) -> list[dict[str, Any]]:
    from application.curriculum.chapters.curriculum_chapter_meta_service import load_chapter_meta_context

    definitions = list_curriculum_collections(language)
    token = activate_showcase_task_index(session)
    batch_token = activate_batch_progress_cache(session, user_id)
    try:
        index = get_showcase_task_index()
        if index is None:
            raise RuntimeError("showcase task index is not active")
        meta_ctx = load_chapter_meta_context(
            session,
            language=language,
            task_counts_by_chapter=index.chapter_task_counts(),
        )
        return _append_custom_chapter_summaries(
            session,
            [
                build_collection_summary_light(
                    session,
                    definition,
                    user_id,
                    index=index,
                    meta_ctx=meta_ctx,
                )
                for definition in definitions
            ],
            language=language,
            meta_ctx=meta_ctx,
        )
    finally:
        reset_batch_progress_cache(batch_token)
        reset_showcase_task_index(token)


def build_global_curriculum_next_from_summaries(
    summaries: list[dict[str, Any]],
) -> dict[str, Any]:
    if not summaries:
        return {
            "next_task": None,
            "collection": None,
            "completed": True,
            "button_label": "Все темы пройдены",
            "progress": {"total_tasks": 0, "passed_tasks": 0, "progress_percent": 0.0},
        }

    aggregate_progress = _aggregate_progress(summaries)
    aggregate_total = aggregate_progress["total_tasks"]
    aggregate_passed = aggregate_progress["passed_tasks"]
    first_incomplete = next((item for item in summaries if not item["completed"]), None)

    if first_incomplete is not None:
        return {
            "next_task": first_incomplete["next_task"],
            "collection": _collection_ref_from_summary(first_incomplete),
            "completed": False,
            "button_label": _global_button_label(
                passed_tasks=aggregate_passed,
                total_tasks=aggregate_total,
                completed=False,
            ),
            "progress": aggregate_progress,
        }

    first_summary = summaries[0]
    all_completed = aggregate_passed >= aggregate_total and aggregate_total > 0
    return {
        "next_task": first_summary["next_task"],
        "collection": _collection_ref_from_summary(first_summary),
        "completed": all_completed,
        "button_label": _global_button_label(
            passed_tasks=aggregate_passed,
            total_tasks=aggregate_total,
            completed=all_completed,
        ),
        "progress": aggregate_progress,
    }


def _collections_view_from_summaries(
    summaries: list[dict[str, Any]],
    *,
    session: Session | None = None,
) -> dict[str, Any]:
    by_language: dict[str, list[dict[str, Any]]] = {}
    for item in summaries:
        by_language.setdefault(item["language"], []).append(item)

    languages: list[dict[str, Any]] = []
    for lang_def in list_home_languages():
        lang = lang_def.language
        collections = by_language.get(lang, [])
        from application.curriculum.showcase.showcase_language_progress import language_is_available

        language_label = lang_def.language_label
        track_description_ru = ""
        if session is not None:
            from application.curriculum.chapters.curriculum_chapter_meta_service import (
                resolve_collection_display,
            )

            language_label, track_description_ru = resolve_collection_display(session, lang)

        languages.append(
            {
                "language": lang,
                "language_label": language_label,
                "track_description_ru": track_description_ru or None,
                "available": language_is_available(collections)
                or bool(list_curriculum_collections(lang)),
                "progress": _aggregate_progress(collections),
                "collections": collections,
            }
        )

    platform_course = None
    if session is not None:
        from application.curriculum.chapters.curriculum_chapter_meta_service import get_platform_course_meta

        meta = get_platform_course_meta(session)
        platform_course = {
            "title": meta["title"],
            "description": meta.get("description") or "",
            "author_user_id": meta.get("author_user_id"),
            "author_name": meta.get("author_name"),
        }

    return {
        "languages": languages,
        # Flat list kept for backward compatibility with older clients.
        "collections": summaries,
        "platform_course": platform_course,
    }


def _enrich_first_incomplete_collection_next(
    session: Session,
    user_id: int | None,
    summaries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Resolve next_task for the first incomplete collection only (keeps light mode fast)."""
    if not summaries:
        return summaries
    target_idx = next((i for i, item in enumerate(summaries) if not item.get("completed")), None)
    if target_idx is None:
        return summaries
    item = summaries[target_idx]
    if item.get("next_task"):
        return summaries
    definition = get_collection_by_id(str(item["collection_id"]))
    if definition is None:
        return summaries

    token = activate_showcase_task_index(session)
    batch_token = activate_batch_progress_cache(session, user_id)
    try:
        full_summary = build_collection_summary(session, definition, user_id)
    finally:
        reset_batch_progress_cache(batch_token)
        reset_showcase_task_index(token)

    updated = list(summaries)
    updated[target_idx] = {
        **item,
        "next_task": full_summary.get("next_task"),
        "button_label": full_summary.get("button_label", item.get("button_label")),
    }
    return updated


def build_curriculum_collections_view(
    session: Session,
    user_id: int | None,
    *,
    language: str | None = None,
    light: bool = False,
) -> dict[str, Any]:
    if light:
        summaries = _build_all_collection_summaries_light(session, user_id, language=language)
        if language:
            summaries = _enrich_first_incomplete_collection_next(session, user_id, summaries)
    else:
        summaries = _build_all_collection_summaries(session, user_id, language=language)
    return _collections_view_from_summaries(summaries, session=session)


def build_curriculum_home_view(session: Session, user_id: int | None) -> dict[str, Any]:
    summaries = _build_all_collection_summaries_light(session, user_id)
    return {
        **_collections_view_from_summaries(summaries, session=session),
        "next": build_global_curriculum_next(session, user_id),
    }


def build_global_curriculum_next(session: Session, user_id: int | None) -> dict[str, Any]:
    light_summaries = _build_all_collection_summaries_light(session, user_id)
    if not light_summaries:
        return build_global_curriculum_next_from_summaries(light_summaries)

    aggregate_progress = _aggregate_progress(light_summaries)
    first_incomplete = next((item for item in light_summaries if not item["completed"]), None)
    if first_incomplete is None:
        return build_global_curriculum_next_from_summaries(light_summaries)

    definition = get_collection_by_id(str(first_incomplete["collection_id"]))
    if definition is None:
        return build_global_curriculum_next_from_summaries(light_summaries)

    token = activate_showcase_task_index(session)
    batch_token = activate_batch_progress_cache(session, user_id)
    try:
        full_summary = build_collection_summary(session, definition, user_id)
    finally:
        reset_batch_progress_cache(batch_token)
        reset_showcase_task_index(token)

    return {
        "next_task": full_summary["next_task"],
        "collection": _collection_ref_from_summary(first_incomplete),
        "completed": False,
        "button_label": _global_button_label(
            passed_tasks=aggregate_progress["passed_tasks"],
            total_tasks=aggregate_progress["total_tasks"],
            completed=False,
        ),
        "progress": aggregate_progress,
    }
