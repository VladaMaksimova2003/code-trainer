"""Teacher authoring for debug (исправление) tasks — fixed vs buggy reference code."""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from application.tasks.services.teacher_assembly_preservation import mark_teacher_assembly_override
from application.tasks.use_cases.debug_code_keys import (
    KNOWN_DEBUG_LANGS,
    buggy_code_key,
    is_buggy_code_key,
    migrate_legacy_starter_to_buggy,
    read_teacher_buggy_code,
)
from application.curriculum.content.v4_code_format import normalize_authoring_code
from application.curriculum.mirror.pedagogical_task_model import available_language_tracks
from infrastructure.db.models.task import Task as TaskModel

_KNOWN_LANGS = KNOWN_DEBUG_LANGS
_RESERVED = frozenset({"patterns", "expected_concepts", "curriculum_showcase", "teacher_assembly_override"})


def _showcase(row: TaskModel) -> dict[str, Any]:
    raw = (row.code_examples or {}).get("curriculum_showcase")
    return dict(raw) if isinstance(raw, dict) else {}


def _is_debug_task(row: TaskModel) -> bool:
    showcase = _showcase(row)
    task_format = str(showcase.get("task_format") or "")
    action = str(showcase.get("primary_action") or "").lower()
    return task_format in {"исправление", "поиск_ошибки"} or action == "debug"


def _can_promote_to_debug(row: TaskModel) -> bool:
    if _is_debug_task(row):
        return True
    if row.translation_task is not None:
        return True
    task_type = str(row.task_type or "").lower()
    try:
        from shared.enums import AssignmentType

        return AssignmentType.parse(task_type).is_translation()
    except ValueError:
        return task_type in {
            "translation",
            "translation_task",
            "task_translate_snippet",
            "task_translate_full_program",
        }


def promote_to_debug_task(row: TaskModel) -> None:
    if _is_debug_task(row):
        return

    from application.curriculum.display.chapter_task_display_order import merge_showcase_preserving_order

    examples = dict(row.code_examples or {})
    showcase = merge_showcase_preserving_order(_showcase(row), dict(_showcase(row)))
    showcase["primary_action"] = "debug"
    showcase["task_format"] = "исправление"

    relation = row.translation_task
    langs = _languages_for_task(row)
    if relation is not None:
        rel_lang = str(relation.source_language or "python").lower()
        if rel_lang not in langs:
            langs.insert(0, rel_lang)
    if not langs:
        langs = ["python"]

    for lang in langs:
        fixed = str(examples.get(lang) or "").strip()
        if not fixed and relation is not None and str(relation.source_language or "").lower() == lang:
            fixed = str(relation.source_code or "").strip()
            if fixed:
                examples[lang] = fixed

        if read_teacher_buggy_code(examples, showcase, lang).strip():
            continue
        buggy = fixed
        if not buggy and relation is not None and str(relation.source_language or "").lower() == lang:
            buggy = str(relation.source_code or "").strip()
        if buggy:
            examples[buggy_code_key(lang)] = buggy

    examples["curriculum_showcase"] = showcase
    row.code_examples = examples


def demote_from_debug_task(row: TaskModel) -> None:
    if not _is_debug_task(row):
        return

    from application.curriculum.display.chapter_task_display_order import merge_showcase_preserving_order

    examples = dict(row.code_examples or {})
    showcase = merge_showcase_preserving_order(_showcase(row), dict(_showcase(row)))
    showcase["primary_action"] = "implement"
    showcase.pop("task_format", None)
    for key in list(showcase.keys()):
        if str(key).startswith("starter_"):
            del showcase[key]
    for key in list(examples.keys()):
        if is_buggy_code_key(str(key)):
            del examples[key]
    examples["curriculum_showcase"] = showcase
    row.code_examples = examples


def _ensure_debug_task_row(db: Session, row: TaskModel) -> bool:
    if _is_debug_task(row):
        return True
    if not _can_promote_to_debug(row):
        return False
    promote_to_debug_task(row)
    mark_teacher_assembly_override(row)
    db.commit()
    db.refresh(row)
    return True


def _languages_for_task(row: TaskModel) -> list[str]:
    showcase = _showcase(row)
    tracks = available_language_tracks(showcase) if showcase else []
    langs: set[str] = set()
    if tracks:
        langs.update(lang for lang in tracks if lang in _KNOWN_LANGS)

    examples = dict(row.code_examples or {})
    for key, value in examples.items():
        if key in _RESERVED or is_buggy_code_key(str(key)):
            if is_buggy_code_key(str(key)) and str(value or "").strip():
                langs.add(str(key).removeprefix("buggy_").lower())
            continue
        lang = str(key).lower()
        if lang in _KNOWN_LANGS and isinstance(value, str) and str(value).strip():
            langs.add(lang)

    block_starters = bool(examples.get("teacher_assembly_override"))
    for key, value in showcase.items():
        if block_starters:
            break
        if not str(key).startswith("starter_"):
            continue
        lang = str(key).removeprefix("starter_").lower()
        if lang in _KNOWN_LANGS and str(value or "").strip():
            langs.add(lang)

    if langs:
        return [lang for lang in _KNOWN_LANGS if lang in langs]
    return list(_KNOWN_LANGS)


def _code_from_examples(examples: dict[str, Any], language: str) -> str:
    return str(examples.get(language) or "")


def _has_teacher_debug_content(examples: dict[str, Any], showcase: dict[str, Any]) -> bool:
    if examples.get("teacher_assembly_override"):
        return True
    for lang in _KNOWN_LANGS:
        if str(examples.get(lang) or "").strip():
            return True
        if str(examples.get(buggy_code_key(lang)) or "").strip():
            return True
        if not examples.get("teacher_assembly_override") and str(
            showcase.get(f"starter_{lang}") or ""
        ).strip():
            return True
    return False


def _maybe_persist_legacy_migration(db: Session, row: TaskModel) -> None:
    examples = dict(row.code_examples or {})
    showcase = _showcase(row)
    if not migrate_legacy_starter_to_buggy(examples, showcase):
        return
    row.code_examples = examples
    flag_modified(row, "code_examples")
    db.commit()
    db.refresh(row)


def get_debug_codes_authoring(db: Session, task_id: int) -> dict[str, Any] | None:
    row = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.is_delete == False).first()
    if row is None:
        return None
    if not _ensure_debug_task_row(db, row):
        return None

    _maybe_persist_legacy_migration(db, row)

    examples = dict(row.code_examples or {})
    showcase = _showcase(row)
    allow_legacy_starter = not bool(examples.get("teacher_assembly_override"))
    slot_id = str(showcase.get("slot_id") or showcase.get("slug") or "").strip()
    languages = _languages_for_task(row)
    use_catalog = not _has_teacher_debug_content(examples, showcase)

    fixed_codes: dict[str, str] = {}
    buggy_codes: dict[str, str] = {}
    for lang in languages:
        fixed = _code_from_examples(examples, lang)
        if not fixed.strip() and use_catalog:
            from application.curriculum.content.algo_syntax_task_extra import (
                algo_fixed_code,
                is_algo_syntax_slot,
            )

            if slot_id and is_algo_syntax_slot(slot_id):
                fixed = str(algo_fixed_code(slot_id, lang) or "")
        fixed_codes[lang] = normalize_authoring_code(fixed) if fixed else ""

        buggy = read_teacher_buggy_code(
            examples,
            showcase,
            lang,
            allow_legacy_starter=allow_legacy_starter,
        )
        if not buggy.strip() and use_catalog:
            from application.curriculum.content.algo_syntax_task_extra import (
                algo_debug_starter,
                is_algo_syntax_slot,
            )

            if slot_id and is_algo_syntax_slot(slot_id):
                buggy = str(algo_debug_starter(slot_id, lang) or "")
        buggy_codes[lang] = normalize_authoring_code(buggy) if buggy else ""

    return {
        "task_id": row.id,
        "slot_id": slot_id or None,
        "languages": languages,
        "fixed_codes": fixed_codes,
        "buggy_codes": buggy_codes,
    }


def update_debug_codes(
    db: Session,
    task_id: int,
    *,
    fixed_codes: dict[str, str] | None = None,
    buggy_codes: dict[str, str] | None = None,
) -> dict[str, Any] | None:
    row = db.query(TaskModel).filter(TaskModel.id == task_id, TaskModel.is_delete == False).first()
    if row is None:
        return None
    if not _ensure_debug_task_row(db, row):
        return None

    examples = dict(row.code_examples or {})
    showcase = _showcase(row)

    if fixed_codes:
        for lang, code in fixed_codes.items():
            lang_key = str(lang).lower()
            if lang_key in _RESERVED:
                continue
            text = str(code or "")
            if text.strip():
                examples[lang_key] = text
            elif lang_key in examples:
                del examples[lang_key]

    if buggy_codes:
        for lang, code in buggy_codes.items():
            lang_key = str(lang).lower()
            if lang_key not in _KNOWN_LANGS:
                continue
            text = str(code or "")
            buggy_key = buggy_code_key(lang_key)
            legacy_key = f"starter_{lang_key}"
            if text.strip():
                examples[buggy_key] = text
            elif buggy_key in examples:
                del examples[buggy_key]
            showcase.pop(legacy_key, None)

    examples["curriculum_showcase"] = showcase
    row.code_examples = examples
    flag_modified(row, "code_examples")

    relation = row.translation_task
    if relation is not None and fixed_codes:
        primary = str(relation.source_language or "python").lower()
        primary_code = str(fixed_codes.get(primary) or examples.get(primary) or "")
        if primary_code.strip():
            relation.source_code = primary_code

    mark_teacher_assembly_override(row)
    from application.tasks.services.task_version_service import record_task_version_after_edit

    db.flush()
    record_task_version_after_edit(db, task_id)
    db.commit()
    db.refresh(row)
    return get_debug_codes_authoring(db, task_id)
