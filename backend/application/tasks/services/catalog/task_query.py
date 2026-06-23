"""Task query service — DB read operations for tasks."""
from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from application.tasks.services.legacy_task_data import LEGACY_TASKS_DB
from application.tasks.services.flowchart_diagram_storage import (
    extract_diagram_from_flow_spec,
    flow_spec_without_diagram_keys,
)
from infrastructure.db.models.task import Task as TaskModel
from shared.enums import AssignmentType

_MOJIBAKE_MARKERS = ("РЎ", "Рќ", "Рџ", "РІС", "Р°Р", "СѓР", "С‡Р")


def _has_mojibake_markers(text: str) -> bool:
    return any(marker in text for marker in _MOJIBAKE_MARKERS)


def _fix_mojibake(text: str | None) -> str | None:
    if text is None or not isinstance(text, str) or not text:
        return text
    has_raw_bytes = any(ord(ch) < 256 and ord(ch) >= 0x80 for ch in text)
    if not _has_mojibake_markers(text) and not has_raw_bytes and "Р" not in text:
        return text

    candidates: list[str] = []
    if "Р" in text:
        try:
            candidates.append(text.encode("cp1251").decode("utf-8"))
        except (UnicodeEncodeError, UnicodeDecodeError):
            pass

    buf = bytearray()
    for ch in text:
        code = ord(ch)
        if code < 256 and not ("\u0400" <= ch <= "\u04FF"):
            buf.append(code)
            continue
        try:
            buf.extend(ch.encode("cp1251"))
        except UnicodeEncodeError:
            buf.extend(ch.encode("utf-8"))
    try:
        candidates.append(buf.decode("utf-8"))
    except UnicodeDecodeError:
        pass

    for candidate in candidates:
        if candidate and candidate != text and not _has_mojibake_markers(candidate):
            return candidate
    return text


def _resolve_task_constructions(
    code_examples: dict[str, Any] | None,
    legacy_constructions: list[str] | None,
) -> list[str]:
    from application.analysis.educational_vocabulary import normalize_construction_tags

    examples = dict(code_examples or {})
    patterns = examples.get("patterns")
    if isinstance(patterns, list) and patterns:
        return normalize_construction_tags([str(item) for item in patterns])
    legacy = legacy_constructions or []
    return normalize_construction_tags([str(item) for item in legacy])


def _pick_construction_hints(constructions: list[str], hints_db: dict) -> dict[str, dict[str, Any]]:
    from infrastructure.analysis.concept_registry import get_concept

    hints: dict[str, dict[str, Any]] = {}
    for concept_id in constructions:
        if concept_id in hints_db:
            hints[concept_id] = hints_db[concept_id]
            continue
        concept = get_concept(concept_id)
        if concept:
            hints[concept_id] = {
                "title": concept.get("name", concept_id),
                "description": concept.get("hint") or concept.get("description", ""),
                "examples": concept.get("patterns", {}),
            }
    return hints


def _sanitize_public_task(task: dict[str, Any]) -> dict[str, Any]:
    from application.curriculum.display.showcase_display import sanitize_public_task_payload

    payload = sanitize_public_task_payload(dict(task))
    if payload.get("type") == "block_reorder":
        payload.pop("original_code", None)
        payload.pop("correct_order", None)
        payload["task_type"] = "block_reorder"
    return payload


def _derive_test_cases_from_python_example(code_examples: dict[str, Any] | None) -> list[dict[str, str]]:
    """No Docker probes on API — use task-stored test cases only."""
    _ = code_examples
    return []


def _task_model_to_dict(task: TaskModel, hints_db: dict, *, sanitize: bool = True) -> dict[str, Any]:
    try:
        parsed = AssignmentType.parse(task.task_type)
        task_type = "blocks" if parsed == AssignmentType.TASK_FLOWCHART_TO_CODE else parsed.value
    except ValueError:
        task_type = "blocks" if task.task_type == "diagram" else task.task_type

    from application.tasks.services.block_reorder_helpers import (
        _decode_newlines,
        is_build_from_blocks_task_type,
    )
    legacy_task = LEGACY_TASKS_DB.get(task.id, {})
    constructions = _resolve_task_constructions(
        task.code_examples,
        legacy_task.get("constructions", []),
    )

    relation_hint = None

    block_reorder_blocks: list[str] = []
    block_reorder_language: str | None = None
    block_reorder_template: str | None = None
    showcase_raw = (task.code_examples or {}).get("curriculum_showcase") if isinstance(task.code_examples, dict) else {}
    showcase_dict = showcase_raw if isinstance(showcase_raw, dict) else {}
    task_format = str(showcase_dict.get("task_format") or "")
    primary_action = str(showcase_dict.get("primary_action") or "").lower()
    is_debug_task = task_format in {"исправление", "поиск_ошибки"} or primary_action == "debug"
    if (
        is_build_from_blocks_task_type(task.task_type)
        and not is_debug_task
        and getattr(task, "block_reorder_task", None)
    ):
        block_reorder_blocks = task.block_reorder_task.blocks or []
        block_reorder_language = task.block_reorder_task.language
        block_reorder_template = _decode_newlines(task.block_reorder_task.template or "")

    code_examples: dict[str, Any] = {}
    for key, value in dict(task.code_examples or {}).items():
        if str(key).lower() == "patterns":
            continue
        if key == "curriculum_showcase" and isinstance(value, dict):
            code_examples[key] = dict(value)
        elif isinstance(value, (list, dict)):
            code_examples[key] = value
        else:
            code_examples[key] = _decode_newlines(value)
    translation = getattr(task, "translation_task", None)
    if translation is not None:
        source_lang = str(translation.source_language or "").lower()
        source_code = _decode_newlines(translation.source_code or "")
        if source_lang and source_code and source_lang not in code_examples:
            code_examples[source_lang] = source_code

    solution_description = (
        relation_hint or legacy_task.get("solution_description") or legacy_task.get("algorithm_hint")
    )
    test_cases = list(task.test_cases or [])
    if not test_cases:
        test_cases = list(legacy_task.get("test_cases") or [])
    if task_type == "blocks" and not test_cases:
        test_cases = _derive_test_cases_from_python_example(task.code_examples or {})

    diagram_payload = extract_diagram_from_flow_spec(task.flow_spec)
    if not diagram_payload.get("nodes") and not diagram_payload.get("edges"):
        diagram_payload = {}

    from application.execution.services.flow_block_constructions import DEFAULT_ALLOWED_BLOCKS

    flow_spec = flow_spec_without_diagram_keys(task.flow_spec)
    if not flow_spec.get("allowed_blocks"):
        flow_spec["allowed_blocks"] = list(DEFAULT_ALLOWED_BLOCKS)

    if diagram_payload:
        student_langs = flow_spec.get("student_reference_languages")
        if isinstance(student_langs, list) and student_langs:
            allowed = {str(lang).lower() for lang in student_langs if str(lang).strip()}
            code_examples = {
                key: value
                for key, value in code_examples.items()
                if str(key).lower() in allowed
            }
        else:
            code_examples = {}

    authoring_language = block_reorder_language
    if not authoring_language and translation is not None:
        authoring_language = str(translation.source_language or "").lower() or None
    if not authoring_language and isinstance(flow_spec, dict):
        raw_primary = flow_spec.get("primary_language")
        if raw_primary:
            authoring_language = str(raw_primary).lower()
        else:
            ref_langs = flow_spec.get("student_reference_languages")
            if isinstance(ref_langs, list) and ref_langs:
                authoring_language = str(ref_langs[0]).lower()
    if not authoring_language and code_examples:
        for key, value in code_examples.items():
            if key == "patterns":
                continue
            if key == "curriculum_showcase" and isinstance(value, dict):
                target = str(value.get("target_language") or "").lower()
                if target in {"pascal", "python"}:
                    authoring_language = target
                    break
                continue
            if str(value or "").strip():
                authoring_language = str(key).lower()
                break

    showcase_meta = (task.code_examples or {}).get("curriculum_showcase") or {}
    showcase_target = str(showcase_meta.get("target_language") or "").lower()
    if showcase_target in {"pascal", "python"}:
        authoring_language = showcase_target

    payload = {
        "id": task.id,
        "title": task.title,
        "description": _fix_mojibake(task.description),
        "difficulty": task.difficulty, "type": task_type, "task_type": task_type,
        "solution_description": _fix_mojibake(solution_description),
        "algorithm_hint": _fix_mojibake(solution_description),
        "constructions": constructions,
        "required_structures": constructions,
        "construction_hints": _pick_construction_hints(constructions, hints_db),
        "test_cases": test_cases,
        "code_examples": code_examples,
        "source_code": _decode_newlines(translation.source_code or "") if translation else None,
        "source_language": translation.source_language if translation else None,
        "flow_spec": flow_spec,
        "diagram": diagram_payload,
        "topic_id": task.topic_id,
        "blocks": block_reorder_blocks,
        "language": authoring_language,
        "template": block_reorder_template,
    }
    if sanitize:
        return _sanitize_public_task(payload)
    return payload


class TaskQueryService:
    def __init__(self, hints_db: dict | None = None):
        self._hints_db = hints_db or {}

    def get_task(
        self,
        db: Session | None,
        task_id: int,
        allowed_task_ids: set[int] | None = None,
        *,
        learning_language: str | None = None,
        source_language: str | None = None,
    ) -> dict[str, Any] | None:
        if allowed_task_ids is not None and task_id not in allowed_task_ids:
            return None
        if db is None:
            task = LEGACY_TASKS_DB.get(task_id)
            if not task:
                return None
            constructions = _resolve_task_constructions(
                task.get("code_examples"),
                task.get("constructions", []),
            )
            enriched = dict(task)
            enriched["constructions"] = constructions
            enriched["required_structures"] = constructions
            enriched["construction_hints"] = _pick_construction_hints(constructions, self._hints_db)
            enriched["description"] = _fix_mojibake(enriched.get("description"))
            if "solution_description" in enriched:
                enriched["solution_description"] = _fix_mojibake(
                    enriched.get("solution_description")
                )
            if "algorithm_hint" in enriched:
                enriched["algorithm_hint"] = _fix_mojibake(enriched.get("algorithm_hint"))
            return _sanitize_public_task(enriched)
        stmt = (
            select(TaskModel)
            .where(TaskModel.id == task_id, TaskModel.is_delete == False)
            .options(
                joinedload(TaskModel.translation_task),
                joinedload(TaskModel.block_reorder_task),
            )
        )
        task = db.execute(stmt).scalars().first()
        if not task:
            return None
        payload = _task_model_to_dict(task, self._hints_db, sanitize=False)
        from application.curriculum.display.curriculum_labels import attach_curriculum_display_to_task

        return attach_curriculum_display_to_task(
            db,
            task_id,
            payload,
            learning_language=learning_language,
            source_language=source_language,
            task_row=task,
        )

    def list_tasks(
        self, db: Session | None = None, allowed_task_ids: set[int] | None = None
    ) -> list[dict[str, Any]]:
        if db is None:
            tasks = []
            for task in LEGACY_TASKS_DB.values():
                constructions = _resolve_task_constructions(
                    task.get("code_examples"),
                    task.get("constructions", []),
                )
                enriched = dict(task)
                enriched["constructions"] = constructions
                enriched["required_structures"] = constructions
                enriched["construction_hints"] = _pick_construction_hints(constructions, self._hints_db)
                enriched["description"] = _fix_mojibake(enriched.get("description"))
                if "solution_description" in enriched:
                    enriched["solution_description"] = _fix_mojibake(enriched.get("solution_description"))
                if "algorithm_hint" in enriched:
                    enriched["algorithm_hint"] = _fix_mojibake(enriched.get("algorithm_hint"))
                tasks.append(_sanitize_public_task(enriched))
            return tasks
        stmt = (
            select(TaskModel)
            .where(TaskModel.is_delete == False)
            .options(
                joinedload(TaskModel.translation_task),
                joinedload(TaskModel.block_reorder_task),
            )
            .order_by(TaskModel.id)
        )
        if allowed_task_ids is not None:
            if not allowed_task_ids:
                return []
            stmt = stmt.where(TaskModel.id.in_(allowed_task_ids))
        tasks = db.execute(stmt).scalars().all()
        return [_task_model_to_dict(task, self._hints_db) for task in tasks]
