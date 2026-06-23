"""Block-reorder validation — structural sync, execution via jobs only."""
from __future__ import annotations

from typing import Any

from application.execution.job_service import ExecutionJobService
from application.tasks.services.block_reorder_helpers import (
    build_entity_from_db,
    is_build_from_blocks_task_type,
)
from infrastructure.db.models.task import Task as TaskModel
from shared.enums import TaskType

_WRONG_ORDER_MESSAGE = (
    "Неверный порядок или неверные блоки — проверьте расстановку в пропусках."
)


def _construction_warnings(
    db,
    task_id: int,
    code: str | None,
    language: str | None,
) -> list[dict[str, str]]:
    assembled = str(code or "").strip()
    if not assembled or not task_id:
        return []
    from application.execution.pipeline_runner import WorkerPipelineRunner

    concept_check = None
    if task_id:
        from application.execution.pipeline_runner import WorkerPipelineRunner

        lang = WorkerPipelineRunner._resolve_concept_check_language(
            assembled,
            str(language or "pascal"),
        )
        _, concept_check = WorkerPipelineRunner()._run_expected_concept_checks(
            db,
            int(task_id),
            assembled,
            lang,
        )
    from application.curriculum.validation.expected_concept_checker import (
        format_construction_warning_messages,
    )

    return format_construction_warning_messages(concept_check, tests_passed=False, language=lang)


def _needs_execution_after_assembly(
    entity,
    *,
    is_correct: bool,
    assembled: str | None,
    has_test_cases: bool,
    variant_template: str | None,
) -> bool:
    if not assembled or not str(assembled).strip():
        return False
    template = variant_template or entity.template
    has_slots = bool(template and entity._template_has_slots(template))
    if has_test_cases:
        # Wrong block order still runs tests — pass/fail is decided by execution.
        if is_correct and has_slots:
            return False
        return True
    if not is_correct:
        return False
    if has_slots:
        return False
    return True


def _normalize_assembled(code: str) -> str:
    import re

    return re.sub(r"\s+", " ", str(code or "").strip())


def _expected_assembled_code(
    entity,
    correct_order: list[int],
    language: str | None,
    indents: list[int] | None,
) -> str:
    return entity.build_code(list(correct_order), language, indents).strip()


def _is_structurally_correct(
    entity,
    order: list[int],
    language: str | None,
    indents: list[int] | None,
    assembled_code: str | None,
    correct_order: list[int],
    *,
    variant_template: str | None = None,
) -> bool:
    submitted = (assembled_code or "").strip()
    if not submitted:
        return False

    expected = _expected_assembled_code(entity, correct_order, language, indents)
    if submitted == expected:
        return True
    if _normalize_assembled(submitted) == _normalize_assembled(expected):
        return True

    if not order:
        return False

    template = variant_template or entity.template
    if entity._template_has_slots(template) and entity.validate_answer(
        list(order), language
    ):
        return True

    if not entity.validate_answer(order, language):
        return False

    from_order = entity.build_code(list(order), language, indents).strip()
    if submitted == from_order:
        return True
    return _normalize_assembled(submitted) == _normalize_assembled(from_order)


def validate_block_reorder_structural(
    db,
    task_id: int,
    order: list[int],
    language: str | None = None,
    indents: list[int] | None = None,
    assembled_code: str | None = None,
) -> dict[str, Any] | None:
    task = (
        db.query(TaskModel)
        .filter(TaskModel.id == task_id, TaskModel.is_delete == False)
        .first()
    )
    if not task or not is_build_from_blocks_task_type(task.task_type):
        return None

    relation = task.block_reorder_task
    if not relation:
        return None

    entity = build_entity_from_db(task, relation)
    variant = entity._get_variant(language)
    variant_correct_order = variant["correct_order"]
    variant_template = variant.get("template") or entity.template
    requested_language = (language or entity.language or "").lower()
    has_test_cases = isinstance(task.test_cases, list) and len(task.test_cases) > 0

    submitted_assembled = (assembled_code or "").strip()
    if submitted_assembled:
        order_valid = bool(order) and entity.validate_answer(list(order), language)
        is_correct = _is_structurally_correct(
            entity,
            list(order or []),
            language,
            indents,
            submitted_assembled,
            list(variant_correct_order),
            variant_template=variant_template,
        )
        needs_execution = _needs_execution_after_assembly(
            entity,
            is_correct=is_correct,
            assembled=submitted_assembled,
            has_test_cases=has_test_cases,
            variant_template=variant_template,
        )
        payload = {
            "task_id": task_id,
            "task_type": TaskType.BLOCK_REORDER.value,
            "assembled_code": submitted_assembled,
            "structural_correct": is_correct,
            "partial": entity.validate_partial(order, language) if order else False,
            "message": (
                "Correct solution" if is_correct else _WRONG_ORDER_MESSAGE
            ),
            "has_test_cases": has_test_cases,
            "language": requested_language,
            "test_cases": list(task.test_cases or []) if has_test_cases else [],
            "execution_mode": "tests" if has_test_cases else "compile",
            "needs_execution": needs_execution,
        }
        if not needs_execution:
            payload["construction_warnings"] = _construction_warnings(
                db,
                task_id,
                submitted_assembled,
                requested_language,
            )
        return payload

    is_correct = entity.validate_answer(order, language)
    if not is_correct and not variant_template:
        expected_len = len(variant_correct_order)
        normalized_order = list(order)
        if len(normalized_order) == expected_len and sorted(normalized_order) == list(
            range(expected_len)
        ):
            reconstructed = [variant_correct_order[idx] for idx in normalized_order]
            is_correct = reconstructed == list(range(expected_len))

    assembled = None
    if len(order) == len(variant_correct_order):
        assembled = entity.build_code(order, language, indents)

    message = (
        "Correct solution"
        if is_correct and (not assembled or has_test_cases)
        else (
            "Correct order"
            if is_correct
            else _WRONG_ORDER_MESSAGE
        )
    )

    needs_execution = _needs_execution_after_assembly(
        entity,
        is_correct=is_correct,
        assembled=assembled,
        has_test_cases=has_test_cases,
        variant_template=variant_template,
    )

    return {
        "task_id": task_id,
        "task_type": TaskType.BLOCK_REORDER.value,
        "assembled_code": assembled,
        "structural_correct": is_correct,
        "partial": entity.validate_partial(order, language),
        "message": message,
        "has_test_cases": has_test_cases,
        "language": requested_language,
        "test_cases": list(task.test_cases or []) if has_test_cases else [],
        "execution_mode": "tests" if has_test_cases else "compile",
        "needs_execution": needs_execution,
    }


def enqueue_block_reorder_execution(
    structural: dict[str, Any],
    *,
    user_id: str,
) -> dict[str, Any]:
    if not structural.get("needs_execution"):
        warnings = list(structural.get("construction_warnings") or [])
        test_cases = list(structural.get("test_cases") or [])
        synthetic_results: list[dict[str, Any]] = []
        if structural.get("structural_correct") and test_cases:
            for index, case in enumerate(test_cases, start=1):
                expected = str(
                    case.get("output")
                    or case.get("expected")
                    or case.get("expected_output")
                    or ""
                )
                synthetic_results.append(
                    {
                        "case": index,
                        "status": "PASSED",
                        "inputs": str(case.get("inputs") or case.get("input") or ""),
                        "expected": expected,
                        "actual": expected,
                        "message": "Correct solution.",
                    }
                )
        return {
            "execution_job_id": None,
            "status": "NOT_REQUIRED",
            "correct": structural.get("structural_correct"),
            "structural_correct": structural.get("structural_correct"),
            "partial": structural.get("partial"),
            "assembled_code": structural.get("assembled_code"),
            "message": structural.get("message"),
            "semantic_checked": False,
            "execution_results": synthetic_results,
            "pattern_errors": warnings,
        }

    assembled = structural.get("assembled_code") or ""
    mode = structural.get("execution_mode") or "tests"
    job_service = ExecutionJobService()
    queued = job_service.submit(
        user_id=user_id,
        language_id=structural["language"],
        code=str(assembled),
        op="block_reorder_validate",
        task_id=int(structural["task_id"]),
        test_cases=list(structural.get("test_cases") or []),
        payload={
            "structural": structural,
            "mode": mode,
        },
    )
    return {
        "execution_job_id": queued["job_id"],
        "status": queued["status"],
        "deduplicated": queued.get("deduplicated", False),
        "structural_correct": structural.get("structural_correct"),
        "partial": structural.get("partial"),
        "assembled_code": assembled,
        "message": structural.get("message"),
        "semantic_checked": False,
        "execution_results": [],
    }
