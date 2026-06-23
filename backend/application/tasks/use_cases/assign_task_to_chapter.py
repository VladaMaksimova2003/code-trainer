"""Assign a teacher task to a curriculum collection chapter."""

from __future__ import annotations

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from application.curriculum.chapters.curriculum_chapter_meta_service import list_chapters
from application.curriculum.collections.curriculum_collections_registry import (
    list_curriculum_collections,
)
from application.curriculum.display.chapter_task_display_order import (
    compute_pedagogical_display_order,
    effective_display_order,
    set_chapter_task_order,
)
from application.curriculum.mirror.pedagogical_task_store import (
    attach_unified_showcase_meta,
    invalidate_pedagogical_slot_index_cache,
    iter_showcase_tasks,
)
from application.curriculum.shared.algo_v128_showcase import primary_tc_for_chapter
from application.tasks.services.catalog.task_teacher_list_meta import (
    teacher_list_meta_for_row,
)
from application.tasks.use_cases.validate_task_test_cases import (
    validate_task_test_cases_for_placement,
)
from infrastructure.db.models.task import Task as TaskModel

_LANG_SLOT_PREFIX = {
    "pascal": "pas",
    "python": "py",
    "cpp": "cpp",
    "csharp": "cs",
    "java": "java",
}


def _showcase_group(language: str, chapter_key: str) -> str:
    lang = language.strip().lower()
    if lang == "pascal":
        from application.curriculum.pascal.showcase.pascal_v311_registry import v311_showcase_group

        return v311_showcase_group(chapter_key)
    if lang == "python":
        from application.curriculum.python.showcase.python_v311_registry import v311_showcase_group

        return v311_showcase_group(chapter_key)
    if lang == "cpp":
        from application.curriculum.cpp.showcase.cpp_v311_registry import v311_showcase_group

        return v311_showcase_group(chapter_key)
    if lang == "csharp":
        from application.curriculum.csharp.showcase.csharp_v311_registry import v311_showcase_group

        return v311_showcase_group(chapter_key)
    if lang == "java":
        from application.curriculum.java.showcase.java_v311_registry import v311_showcase_group

        return v311_showcase_group(chapter_key)
    return f"{lang}_curriculum_v311_{chapter_key}"


def _chapter_record(session: Session, language: str, chapter_key: str):
    normalized_lang = language.strip().lower()
    normalized_key = chapter_key.strip()
    for record in list_chapters(session, language=normalized_lang):
        if record.chapter_key == normalized_key:
            return record
    return None


def _collection_id(language: str, chapter_key: str) -> str | None:
    for col in list_curriculum_collections(language.strip().lower()):
        if col.chapter_key == chapter_key:
            return col.collection_id
    lang = language.strip().lower()
    return f"{lang}_{chapter_key}_v311"


def _ordered_task_ids_in_chapter(
    session: Session,
    *,
    teacher_id: int,
    chapter_key: str,
) -> list[int]:
    rows: list[tuple[int, int]] = []
    for row, showcase in iter_showcase_tasks(session):
        if row.teacher_id != teacher_id:
            continue
        if str(showcase.get("collection_key") or "").strip() != chapter_key:
            continue
        rows.append((effective_display_order(showcase), int(row.id)))
    rows.sort(key=lambda item: (item[0], item[1]))
    return [task_id for _, task_id in rows]


def assign_task_to_chapter(
    db: Session,
    *,
    teacher_id: int,
    task_id: int,
    language: str,
    chapter_key: str,
) -> dict[str, str | int]:
    normalized_lang = str(language or "").strip().lower()
    normalized_chapter = str(chapter_key or "").strip()
    if normalized_lang not in _LANG_SLOT_PREFIX:
        raise ValueError(f"Unsupported language: {language}")
    if not normalized_chapter:
        raise ValueError("chapter_key is required")

    chapter = _chapter_record(db, normalized_lang, normalized_chapter)
    if chapter is None:
        raise ValueError("Chapter not found for the selected collection")

    row = db.get(TaskModel, int(task_id))
    if row is None or row.is_delete:
        raise ValueError(f"Task {task_id} not found")
    if row.teacher_id != teacher_id:
        raise ValueError(f"Task {task_id} does not belong to this teacher")

    validate_task_test_cases_for_placement(
        db,
        task_id=int(task_id),
        placement_language=normalized_lang,
        user_id=str(teacher_id),
    )

    meta = teacher_list_meta_for_row(row)
    primary_action = meta.primary_action or "implement"
    slot_prefix = _LANG_SLOT_PREFIX[normalized_lang]
    slot_id = f"{slot_prefix}_teacher_{task_id}"

    track_meta: dict[str, object] = {
        "group": _showcase_group(normalized_lang, normalized_chapter),
        "collection_key": normalized_chapter,
        "slug": slot_id,
        "slot_id": slot_id,
        "curriculum_version": "3.1.1",
        "target_language": normalized_lang,
        "technical_concept_id": primary_tc_for_chapter(normalized_chapter),
        "primary_action": primary_action,
        "task_format": meta.task_format or "",
        "educational_goal": row.description or row.title,
        "pedagogical_slot_id": f"teacher:{task_id}",
        "collection_chapter_rank": chapter.sort_order,
    }
    collection_id = _collection_id(normalized_lang, normalized_chapter)
    if collection_id:
        track_meta["collection_id"] = collection_id

    existing_orders = [
        effective_display_order(showcase)
        for task_row, showcase in iter_showcase_tasks(db)
        if task_row.teacher_id == teacher_id
        and str(showcase.get("collection_key") or "").strip() == normalized_chapter
        and int(task_row.id) != int(task_id)
    ]
    next_order = (max(existing_orders) if existing_orders else 0) + 10
    if next_order >= 999_999:
        next_order = compute_pedagogical_display_order(
            title=str(row.title or ""),
            action=primary_action,
            task_num=int(task_id),
        )
    track_meta["display_order"] = next_order

    attach_unified_showcase_meta(row, track_meta, normalized_lang)  # type: ignore[arg-type]
    flag_modified(row, "code_examples")
    db.flush()

    ordered_ids = _ordered_task_ids_in_chapter(
        db,
        teacher_id=teacher_id,
        chapter_key=normalized_chapter,
    )
    if int(task_id) not in ordered_ids:
        ordered_ids.append(int(task_id))
    set_chapter_task_order(
        db,
        teacher_id=teacher_id,
        chapter_key=normalized_chapter,
        ordered_task_ids=ordered_ids,
    )

    invalidate_pedagogical_slot_index_cache()
    from application.curriculum.showcase.showcase_task_index import invalidate_showcase_task_index_cache

    invalidate_showcase_task_index_cache()

    return {
        "task_id": int(task_id),
        "language": normalized_lang,
        "chapter_key": normalized_chapter,
        "chapter_title": chapter.title,
    }
