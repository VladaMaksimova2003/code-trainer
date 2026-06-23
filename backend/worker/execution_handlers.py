"""Worker-only execution handlers (Docker via ExecutionCore)."""
from __future__ import annotations

from typing import Any

from application.execution.pipeline_runner import WorkerPipelineRunner
from application.execution.services.flow_validation_service import FlowValidationService
from infrastructure.execution.execution_core import ExecutionCore
from worker.submission_store import SubmissionStore

_core = ExecutionCore()
_pipeline = WorkerPipelineRunner()
_flow = FlowValidationService()
_submissions = SubmissionStore()


def handle_compile_check(job) -> dict[str, Any]:
    errors = _core.compile_check(job.language_id, job.code)
    return {"errors": errors}


def handle_run_tests(job) -> dict[str, Any]:
    results = _core.run_tests(job.language_id, job.code, job.test_cases)
    return {"test_results": [r.to_dict() for r in results]}


def handle_block_reorder_validate(job) -> dict[str, Any]:
    structural = dict(job.payload.get("structural") or {})
    mode = str(job.payload.get("mode") or "tests")
    test_cases = job.test_cases
    code = job.code
    lang = job.language_id
    task_id = int(getattr(job, "task_id", 0) or job.payload.get("task_id") or 0)

    semantic_checked = False
    execution_results: list[dict[str, Any]] = []
    construction_warnings: list[dict[str, str]] = []
    concept_check = None
    semantic_message = structural.get("message")
    is_correct = bool(structural.get("structural_correct"))
    executable = code

    if task_id:
        from application.curriculum.validation.expected_concept_checker import (
            format_construction_warning_messages,
        )
        from application.execution.pipeline_runner import _task_db_session

        lang = WorkerPipelineRunner._resolve_concept_check_language(code, lang)
        with _task_db_session() as db:
            _, concept_check = WorkerPipelineRunner()._run_expected_concept_checks(
                db, task_id, code, lang
            )
            if mode == "tests" and test_cases:
                executable = WorkerPipelineRunner()._prepare_code_for_execution(
                    db, task_id, code, lang
                )

    if not test_cases:
        test_cases = list(structural.get("test_cases") or [])

    if mode == "tests" and test_cases:
        compile_errors = _core.compile_check(lang, executable)
        if compile_errors:
            execution_results = [
                {
                    "case": index,
                    "status": "ERROR",
                    "inputs": str(
                        case.get("inputs") or case.get("input") or ""
                    ),
                    "expected": str(
                        case.get("output")
                        or case.get("expected")
                        or case.get("expected_output")
                        or ""
                    ),
                    "actual": "",
                    "message": compile_errors[0],
                }
                for index, case in enumerate(test_cases, start=1)
            ]
            semantic_checked = True
            is_correct = False
            semantic_message = compile_errors[0]
        else:
            results = _core.run_tests(lang, executable, test_cases)
            execution_results = [r.to_dict() for r in results]
            semantic_checked = True
            is_correct = bool(results) and all(r.status == "PASSED" for r in results)
            if not is_correct and any(r.status == "ERROR" for r in results):
                semantic_message = "Code has runtime/syntax errors for test cases"
            elif not is_correct:
                semantic_message = "Incorrect output for expected test cases"
    elif mode == "compile":
        errors = _core.compile_check(lang, code)
        semantic_checked = True
        if errors:
            is_correct = False
            semantic_message = errors[0]
        else:
            is_correct = False
            semantic_message = (
                semantic_message
                or "Тестовые данные не были выполнены, проверка по синтаксису не засчитывается"
            )

    if task_id and concept_check:
        construction_warnings = format_construction_warning_messages(
            concept_check,
            tests_passed=bool(mode == "tests" and test_cases and is_correct),
            language=lang,
        )

    pattern_errors = list(construction_warnings)
    tests_failed = bool(mode == "tests" and test_cases and execution_results and not is_correct)
    if task_id and tests_failed:
        from application.execution.pipeline_runner import _task_db_session

        with _task_db_session() as db:
            pattern_errors = _pipeline._append_post_submit_feedback(
                db,
                task_id,
                code,
                lang,
                pattern_errors,
                execution_results,
            )

    return {
        **structural,
        "correct": is_correct,
        "semantic_checked": semantic_checked,
        "execution_results": execution_results,
        "pattern_errors": pattern_errors,
        "message": (
            "Correct solution"
            if is_correct
            else semantic_message or structural.get("message") or "Incorrect solution"
        ),
    }


def handle_flow_semantic_check(job) -> dict[str, Any]:
    test_cases = job.test_cases
    if not test_cases:
        return {
            "errors": [
                {
                    "type": "FLOW_SEMANTIC_NO_TESTS",
                    "text": "Нет тестовых данных для семантической проверки.",
                }
            ],
            "execution_results": [],
            "test_cases": [],
            "semantic_checked": False,
        }

    results = _core.run_tests(job.language_id, job.code, test_cases)
    serialized = _flow._serialize_execution_results(results)

    if results and all(item.status == "PASSED" for item in results):
        return {
            "errors": [],
            "execution_results": serialized,
            "test_cases": test_cases,
            "semantic_checked": True,
        }

    first = results[0] if results else None
    message = (first.message if first else None) or "Собранный код не совпадает с ожидаемым поведением."
    return {
        "errors": [{"type": "FLOW_SEMANTIC_MISMATCH", "text": message}],
        "execution_results": serialized,
        "test_cases": test_cases,
        "semantic_checked": True,
    }


def handle_process_submission(job) -> dict[str, Any]:
    payload = job.payload
    submission_id = int(payload["submission_id"])
    code, language, task_id, _user_id = _submissions.load_for_execution(submission_id)
    result = _pipeline.run_submission(
        task_id=task_id,
        code=code,
        language=language,
    )
    _submissions.persist_success(submission_id=submission_id, result=result)
    return {
        "submission_id": submission_id,
        "status": "done",
        "success": result.get("success"),
    }
