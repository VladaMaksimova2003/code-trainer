"""Task catalog — thin orchestrator.

Actual logic lives in:
  services/legacy_task_data.py  — static fallback task data
  services/task_query.py        — TaskQueryService (DB reads)
  services/block_reorder_helpers.py — block-reorder utilities
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from application.tasks.services.legacy_task_data import LEGACY_TASKS_DB  # noqa: F401
from application.tasks.services.catalog.task_query import TaskQueryService, _pick_construction_hints  # noqa: F401

_CONSTRUCTION_HINTS_PATH = (
    Path(__file__).resolve().parents[4] / "resources" / "construction_hints.json"
)
try:
    with _CONSTRUCTION_HINTS_PATH.open("r", encoding="utf-8") as _f:
        CONSTRUCTION_HINTS_DB: dict[str, dict[str, Any]] = json.load(_f)
except (OSError, json.JSONDecodeError):
    CONSTRUCTION_HINTS_DB = {}

_query_service = TaskQueryService(CONSTRUCTION_HINTS_DB)


def load_construction_hints() -> dict[str, dict[str, Any]]:
    return dict(CONSTRUCTION_HINTS_DB)


def get_task(
    db: Session | None = None,
    task_id: int = 0,
    allowed_task_ids: set[int] | None = None,
    *,
    learning_language: str | None = None,
    source_language: str | None = None,
) -> dict[str, Any] | None:
    return _query_service.get_task(
        db,
        task_id,
        allowed_task_ids,
        learning_language=learning_language,
        source_language=source_language,
    )


def list_tasks(
    db: Session | None = None,
    allowed_task_ids: set[int] | None = None,
) -> list[dict[str, Any]]:
    return _query_service.list_tasks(db, allowed_task_ids)


def list_task_overviews(
    db: Session,
    *,
    allowed_task_ids: set[int] | None = None,
    course: str | None = None,
    chapter: str | None = None,
    target_language: str | None = None,
    search: str | None = None,
    task_type: str | None = None,
    difficulty: str | None = None,
    pattern: str | None = None,
    language: str | None = None,
    restrict_task_ids: set[int] | None = None,
    page: int = 1,
    page_size: int | None = None,
) -> dict[str, Any]:
    from application.tasks.services.catalog.task_overview import list_task_overviews as _list

    return _list(
        db,
        allowed_task_ids=allowed_task_ids,
        course=course,
        chapter=chapter,
        target_language=target_language,
        search=search,
        task_type=task_type,
        difficulty=difficulty,
        pattern=pattern,
        language=language,
        restrict_task_ids=restrict_task_ids,
        page=page,
        page_size=page_size,
    )


def list_task_types() -> list[dict[str, str]]:
    from domain.services.assignment_strategies.registry import list_creatable_assignment_types
    from shared.enums import AssignmentType

    types = list_creatable_assignment_types()
    types.append({
        "id": AssignmentType.LEGACY_ALGORITHM.value,
        "name": AssignmentType.LEGACY_ALGORITHM.public_label(),
    })
    return types


def get_task_constructions(db: Session | None = None, task_id: int = 0) -> list:
    """Return required structures for pattern validation (v2 dict or legacy list)."""
    expected = get_task_expected_concept_ids(db=db, task_id=task_id)
    if expected:
        return expected
    task = get_task(db=db, task_id=task_id)
    if not task:
        return []
    required = task.get("required_structures")
    if isinstance(required, list) and required:
        return required
    return task.get("constructions", [])


def get_task_expected_concept_ids(
    db: Session | None = None,
    task_id: int = 0,
    *,
    language: str | None = None,
) -> list[str]:
    """Per-task expected pedagogical concepts; optional per submission language."""
    lang = str(language or "").strip().lower()

    if db is not None and task_id:
        from infrastructure.db.models.task.registry import load_models
        from infrastructure.db.models.task import Task as TaskModel
        from application.tasks.services.authoring_expected_concepts import (
            resolve_authoring_expected_concepts_by_language,
        )

        load_models()
        row = db.get(TaskModel, task_id)
        if row is not None:
            by_lang = resolve_authoring_expected_concepts_by_language(row.code_examples)
            if lang and lang in by_lang:
                return by_lang[lang]
            if by_lang:
                showcase = (row.code_examples or {}).get("curriculum_showcase") or {}
                primary = str(showcase.get("target_language") or lang or "pascal").lower()
                if primary in by_lang:
                    return by_lang[primary]
                return next(iter(by_lang.values()))

            showcase = (row.code_examples or {}).get("curriculum_showcase") or {}
            if isinstance(showcase, dict):
                raw = showcase.get("expected_concept_ids")
                if isinstance(raw, list) and raw:
                    return [str(item) for item in raw if str(item).strip()]

    task = get_task(db=db, task_id=task_id)
    if not task:
        return []
    for source in (
        task.get("expected_concept_ids"),
        (task.get("curriculum") or {}).get("expected_concept_ids"),
        ((task.get("code_examples") or {}).get("curriculum_showcase") or {}).get(
            "expected_concept_ids"
        )
        if isinstance((task.get("code_examples") or {}).get("curriculum_showcase"), dict)
        else None,
    ):
        if isinstance(source, list) and source:
            return [str(item) for item in source if str(item).strip()]
    return []


def get_task_mirror_context(
    db: Session | None = None,
    task_id: int = 0,
    *,
    submission_language: str | None = None,
) -> dict[str, str] | None:
    """Resolve mirror pair (source example language, target track language) for a task."""
    lang = str(submission_language or "").strip().lower()
    if lang in {"cs", "c#"}:
        lang = "csharp"

    if db is not None and task_id:
        from infrastructure.db.models.task.registry import load_models
        from infrastructure.db.models.task import Task as TaskModel

        load_models()
        row = db.get(TaskModel, task_id)
        if row is not None:
            examples = dict(row.code_examples or {})
            showcase = examples.get("curriculum_showcase") or {}
            if isinstance(showcase, dict):
                target = str(
                    showcase.get("target_language")
                    or showcase.get("language")
                    or lang
                    or row.language
                    or ""
                ).lower()
                if target in {"cs", "c#"}:
                    target = "csharp"
                source = str(showcase.get("source_language") or "").lower()
                if source in {"cs", "c#"}:
                    source = "csharp"
                if not source:
                    translation = getattr(row, "translation_task", None)
                    if translation is not None:
                        source = str(translation.source_language or "").lower()
                if not source and target == "pascal":
                    source = "python"
                if not source and target == "python":
                    source = "pascal"
                if source and target:
                    return {"source_language": source, "target_language": target}

    task = get_task(db=db, task_id=task_id)
    if not task:
        return None
    showcase = (task.get("code_examples") or {}).get("curriculum_showcase") or {}
    if not isinstance(showcase, dict):
        return None
    target = str(
        showcase.get("target_language") or task.get("language") or lang or "pascal"
    ).lower()
    if target in {"cs", "c#"}:
        target = "csharp"
    source = str(showcase.get("source_language") or task.get("source_language") or "").lower()
    if source in {"cs", "c#"}:
        source = "csharp"
    if not source:
        source = str(task.get("source_language") or "").lower()
    if not source and target == "pascal":
        source = "python"
    if not source and target == "python":
        source = "pascal"
    if not source or not target:
        return None
    return {"source_language": source, "target_language": target}


def get_task_test_cases(db: Session | None = None, task_id: int = 0) -> list[dict[str, str]]:
    task = get_task(db=db, task_id=task_id)
    return task.get("test_cases", []) if task else []


def is_snippet_translation_task(db: Session | None = None, task_id: int = 0) -> bool:
    task = get_task(db=db, task_id=task_id)
    return bool(task and task.get("type") == "task_translate_snippet")


_NON_CODE_TASK_FORMATS = frozenset(
    {
        "выбор_фрагмента",
        "блок-схема_по_коду",
        "поиск_ошибки",
    }
)


def _task_row(db: Session, task_id: int):
    from infrastructure.db.models.task.registry import load_models
    from infrastructure.db.models.task import Task as TaskModel

    load_models()
    return db.get(TaskModel, task_id)


def get_task_showcase_meta(db: Session | None = None, task_id: int = 0) -> dict[str, Any]:
    if db is None or not task_id:
        return {}
    row = _task_row(db, task_id)
    if row is None:
        return {}
    showcase = (row.code_examples or {}).get("curriculum_showcase") or {}
    return dict(showcase) if isinstance(showcase, dict) else {}


def is_mcq_task(db: Session | None = None, task_id: int = 0) -> bool:
    if db is None or not task_id:
        task = get_task(db=db, task_id=task_id)
        flow_spec = dict((task or {}).get("flow_spec") or {})
        return bool(flow_spec.get("mcq_mode"))
    row = _task_row(db, task_id)
    if row is None:
        return False
    flow_spec = dict(row.flow_spec or {})
    return bool(flow_spec.get("mcq_mode"))


def get_task_mcq_spec(db: Session | None = None, task_id: int = 0) -> dict[str, Any] | None:
    if db is None or not task_id:
        task = get_task(db=db, task_id=task_id)
        if not task or not is_mcq_task(db=db, task_id=task_id):
            return None
        examples = dict(task.get("code_examples") or {})
        flow_spec = dict(task.get("flow_spec") or {})
        options = examples.get("mcq_options")
        if not isinstance(options, list) or not options:
            return None
        correct_index = examples.get("mcq_correct_index", flow_spec.get("correct_index", 0))
        return {
            "options": [str(item) for item in options],
            "correct_index": int(correct_index or 0),
            "explanation": flow_spec.get("explanation"),
        }

    row = _task_row(db, task_id)
    if row is None or not is_mcq_task(db=db, task_id=task_id):
        return None
    examples = dict(row.code_examples or {})
    flow_spec = dict(row.flow_spec or {})
    options = examples.get("mcq_options")
    if not isinstance(options, list) or not options:
        return None
    correct_index = examples.get("mcq_correct_index", flow_spec.get("correct_index", 0))
    return {
        "options": [str(item) for item in options],
        "correct_index": int(correct_index or 0),
        "explanation": flow_spec.get("explanation"),
    }


def should_skip_expected_concept_checks(db: Session | None = None, task_id: int = 0) -> bool:
    if is_mcq_task(db=db, task_id=task_id):
        return True
    showcase = get_task_showcase_meta(db=db, task_id=task_id)
    task_format = str(showcase.get("task_format") or "").strip()
    return task_format in _NON_CODE_TASK_FORMATS


def get_task_flow_spec(db: Session | None = None, task_id: int = 0) -> dict[str, Any]:
    task = get_task(db=db, task_id=task_id)
    return task.get("flow_spec", {}) if task else {}


def get_task_pattern_key(db: Session | None = None, task_id: int = 0) -> str | None:
    """task_NNN pattern for algorithm-syntax catalog lookup."""
    showcase = get_task_showcase_meta(db=db, task_id=task_id)
    for key in ("slot_pattern_id", "exercise_pattern_id", "pattern_id"):
        raw = str(showcase.get(key) or "").strip()
        if raw.startswith("task_"):
            return raw
    if db is not None and task_id:
        row = _task_row(db, task_id)
        if row is not None:
            from infrastructure.db.models.task.task_curriculum_link import TaskCurriculumLinkModel

            link = (
                db.query(TaskCurriculumLinkModel)
                .filter(TaskCurriculumLinkModel.task_id == task_id, TaskCurriculumLinkModel.is_primary.is_(True))
                .first()
            )
            if link is None:
                link = (
                    db.query(TaskCurriculumLinkModel)
                    .filter(TaskCurriculumLinkModel.task_id == task_id)
                    .order_by(TaskCurriculumLinkModel.id.asc())
                    .first()
                )
            if link is not None:
                pat = str(link.exercise_pattern_id or "").strip()
                if pat.startswith("task_"):
                    return pat
    return None


def get_task_pitfall_meta(db: Session | None = None, task_id: int = 0) -> dict[str, Any]:
    pattern = get_task_pattern_key(db=db, task_id=task_id)
    if not pattern:
        return {}
    from application.curriculum.content.algo_syntax_task_extra import algo_pitfall_meta_by_pattern

    meta = algo_pitfall_meta_by_pattern(pattern)
    if meta.get("pitfall_id"):
        return meta
    return {}


_legacy_cache: dict[int, dict[str, Any]] = {}


def init_legacy_cache(db: Session) -> None:
    global _legacy_cache
    _legacy_cache = {task["id"]: task for task in list_tasks(db)}


def get_task_legacy(task_id: int) -> dict[str, Any] | None:
    return _legacy_cache.get(task_id)


def list_tasks_legacy() -> list[dict[str, Any]]:
    return list(_legacy_cache.values())
