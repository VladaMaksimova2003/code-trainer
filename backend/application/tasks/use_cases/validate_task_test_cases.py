"""Validate teacher task reference solution against test cases before chapter placement."""

from __future__ import annotations

import time
from typing import Any

from sqlalchemy.orm import Session

from application.execution.job_service import ExecutionJobService
from application.tasks.services.block_reorder_helpers import (
    build_entity_from_db,
    is_build_from_blocks_task_type,
)
from application.tasks.services.catalog.task_teacher_list_meta import teacher_list_meta_for_row
from application.tasks.use_cases.block_reorder.validate import validate_block_reorder_solution
from application.tasks.use_cases.debug_code_keys import is_buggy_code_key
from infrastructure.db.models.task import Task as TaskModel
from shared.enums import AssignmentType

_RESERVED_EXAMPLE_KEYS = frozenset(
    {"patterns", "expected_concepts", "curriculum_showcase", "teacher_assembly_override"}
)


def _normalize_test_cases(raw: object) -> list[dict[str, Any]]:
    if not isinstance(raw, list):
        return []
    return [dict(item) for item in raw if isinstance(item, dict)]


def _resolve_language(row: TaskModel, placement_language: str) -> str:
    lang = str(placement_language or "").strip().lower()
    if lang:
        return lang

    relation = row.block_reorder_task
    if relation is not None and str(relation.language or "").strip():
        return str(relation.language).strip().lower()

    translation = row.translation_task
    if translation is not None and str(translation.source_language or "").strip():
        return str(translation.source_language).strip().lower()

    examples = dict(row.code_examples or {})
    for key, value in examples.items():
        key_text = str(key)
        if key in _RESERVED_EXAMPLE_KEYS or is_buggy_code_key(key_text):
            continue
        if isinstance(value, str) and value.strip():
            return key_text.lower()

    return "python"


def _fixed_reference_code(row: TaskModel, language: str) -> str:
    """Reference solution for placement validation (never buggy starter code)."""
    lang = str(language).lower()
    examples = dict(row.code_examples or {})

    fixed = str(examples.get(lang) or "").strip()
    if fixed:
        return fixed

    translation = row.translation_task
    if translation is not None and str(translation.source_language or "").lower() == lang:
        return str(translation.source_code or "").strip()

    relation = row.block_reorder_task
    if relation is not None and str(relation.original_code or "").strip():
        if str(relation.language or "python").lower() == lang:
            return str(relation.original_code or "").strip()

    return ""


def _block_assembled_code(row: TaskModel, language: str) -> str:
    relation = row.block_reorder_task
    if relation is None:
        return ""
    entity = build_entity_from_db(row, relation)
    variant = entity._get_variant(language)
    correct_order = list(variant.get("correct_order") or relation.correct_order or [])
    if not correct_order:
        return ""
    return entity.build_code(correct_order, language, None).strip()


def _resolve_reference_code(row: TaskModel, *, language: str, is_debug: bool) -> str:
    if is_build_from_blocks_task_type(str(row.task_type or "")):
        assembled = _block_assembled_code(row, language)
        if assembled:
            return assembled

    if is_debug:
        return _fixed_reference_code(row, language)

    try:
        parsed = AssignmentType.parse(str(row.task_type or ""))
    except ValueError:
        parsed = None

    if parsed is not None and parsed == AssignmentType.TASK_FLOWCHART_TO_CODE:
        flow_spec = dict(row.flow_spec or {})
        student_langs = flow_spec.get("student_reference_languages") or []
        primary = str(student_langs[0] if student_langs else language).lower()
        examples = dict(row.code_examples or {})
        for candidate in (primary, language):
            code = str(examples.get(candidate) or "").strip()
            if code:
                return code
        for key, value in examples.items():
            if key in _RESERVED_EXAMPLE_KEYS or is_buggy_code_key(str(key)):
                continue
            text = str(value or "").strip()
            if text:
                return text

    return _fixed_reference_code(row, language)


def _failed_test_message(results: list[dict[str, Any]]) -> str:
    for item in results:
        if str(item.get("status") or "").upper() != "PASSED":
            case_num = item.get("case") or "?"
            message = str(item.get("message") or "").strip()
            if message:
                return f"Тест {case_num} не пройден: {message}"
            expected = str(item.get("expected") or "").strip()
            actual = str(item.get("actual") or "").strip()
            if expected or actual:
                return (
                    f"Тест {case_num} не пройден: ожидалось «{expected}», получено «{actual}»"
                )
            return f"Тест {case_num} не пройден"
    return "Эталонный код не прошёл тестовые случаи"


def _assert_execution_results_passed(result: dict[str, Any]) -> None:
    results = list(result.get("execution_results") or result.get("test_results") or [])
    if results:
        if all(str(item.get("status") or "").upper() == "PASSED" for item in results):
            return
        raise ValueError(_failed_test_message(results))

    if result.get("correct") or result.get("structural_correct"):
        return

    message = str(result.get("message") or "").strip()
    raise ValueError(message or "Эталонное решение не прошло проверку")


def _wait_for_job(job_service: ExecutionJobService, job_id: str, *, timeout_sec: float) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_sec
    while time.monotonic() < deadline:
        payload = job_service.get_result(job_id)
        status = str(payload.get("status") or "")
        if status in {"SUCCESS", "FAILED", "TIMEOUT"}:
            return payload
        time.sleep(0.25)
    return {"job_id": job_id, "status": "TIMEOUT", "output": None, "errors": "Timeout"}


def _finalize_async_validation(job_service: ExecutionJobService, queued: dict[str, Any], *, timeout_sec: float) -> None:
    job_id = str(queued.get("execution_job_id") or queued.get("job_id") or "")
    if not job_id:
        _assert_execution_results_passed(queued)
        return

    polled = _wait_for_job(job_service, job_id, timeout_sec=timeout_sec)
    status = str(polled.get("status") or "")
    if status == "TIMEOUT":
        raise ValueError(
            "Проверка тестов заняла слишком много времени. "
            "Убедитесь, что запущен execution worker, и попробуйте снова."
        )
    if status == "FAILED":
        error_text = str(polled.get("errors") or polled.get("error") or "").strip()
        raise ValueError(error_text or "Не удалось выполнить тестовые случаи")

    validation = polled.get("validation") or polled.get("output") or {}
    if not isinstance(validation, dict):
        raise ValueError("Не удалось выполнить тестовые случаи")
    _assert_execution_results_passed(validation)


def validate_task_test_cases_for_placement(
    db: Session,
    *,
    task_id: int,
    placement_language: str,
    user_id: str,
    timeout_sec: float = 90.0,
) -> None:
    """Raise ValueError when reference solution fails test cases or data is incomplete."""
    row = db.get(TaskModel, int(task_id))
    if row is None or row.is_delete:
        raise ValueError(f"Task {task_id} not found")

    test_cases = _normalize_test_cases(row.test_cases)
    if not test_cases:
        raise ValueError("Добавьте тестовые случаи перед размещением задания в главу")

    language = _resolve_language(row, placement_language)
    meta = teacher_list_meta_for_row(row)
    reference_code = _resolve_reference_code(row, language=language, is_debug=meta.is_debug_task)
    if not reference_code.strip():
        if meta.is_debug_task:
            raise ValueError("Укажите правильный код (fixed) перед добавлением в главу")
        raise ValueError("Укажите эталонный код решения перед добавлением в главу")

    job_service = ExecutionJobService()

    if is_build_from_blocks_task_type(str(row.task_type or "")):
        relation = row.block_reorder_task
        if relation is None:
            raise ValueError("Задание на сборку не настроено")
        correct_order = list(relation.correct_order or [])
        queued = validate_block_reorder_solution(
            db,
            int(task_id),
            correct_order,
            language=language,
            assembled_code=reference_code,
            user_id=str(user_id),
        )
        if queued is None:
            raise ValueError("Задание на сборку не найдено")
        _finalize_async_validation(job_service, queued, timeout_sec=timeout_sec)
        return

    queued = job_service.submit(
        user_id=str(user_id),
        language_id=language,
        code=reference_code,
        op="block_reorder_validate",
        task_id=int(task_id),
        test_cases=test_cases,
        payload={
            "structural": {
                "task_id": int(task_id),
                "structural_correct": True,
                "language": language,
                "test_cases": test_cases,
                "execution_mode": "tests",
                "needs_execution": True,
                "assembled_code": reference_code,
                "message": "Reference validation",
            },
            "mode": "tests",
        },
    )
    _finalize_async_validation(
        job_service,
        {"execution_job_id": queued.get("job_id"), "status": queued.get("status")},
        timeout_sec=timeout_sec,
    )
