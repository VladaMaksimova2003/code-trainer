from __future__ import annotations

from typing import Any

from application.execution.dto import CheckSolutionDTO


class SolutionPipelineService:
    def __init__(self, check_use_case: Any, test_runner: Any):
        self._check_use_case = check_use_case
        self._test_runner = test_runner

    def run_full(self, task_id: int, code: str, language: str) -> dict[str, Any]:
        compiler_errors, linter_errors, pattern_errors = self._run_checks(
            task_id,
            code,
            language,
            mode="full",
        )

        test_results = self._run_test_cases(
            task_id=task_id,
            code=code,
            language=language,
            has_compiler_errors=bool(compiler_errors),
        )

        tests_passed = bool(test_results) and all(
            item["status"] == "PASSED" for item in test_results
        )
        success = not compiler_errors and tests_passed

        return {
            "task_id": task_id,
            "success": success,
            "compiler_errors": compiler_errors,
            "linter_errors": linter_errors,
            "pattern_errors": pattern_errors,
            "test_results": test_results,
        }

    def run_lint_only(self, task_id: int, code: str, language: str) -> dict[str, Any]:
        _, linter_errors, _ = self._run_checks(
            task_id, code, language, mode="lint_only"
        )
        return {
            "task_id": task_id,
            "linter_errors": linter_errors,
        }

    def run_pattern_only(
        self, task_id: int, code: str, language: str
    ) -> dict[str, Any]:
        _, _, pattern_errors = self._run_checks(
            task_id, code, language, mode="pattern_only"
        )
        return {
            "task_id": task_id,
            "pattern_errors": pattern_errors,
        }

    def _run_checks(
        self,
        task_id: int,
        code: str,
        language: str,
        mode: str,
    ) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
        from application.tasks.services.catalog.task_catalog_orchestrator import get_task_constructions

        dto = CheckSolutionDTO(
            code=code,
            language=language,
            constructions=get_task_constructions(task_id=task_id),
            task_id=task_id,
            mode=mode,
        )
        check_result = self._check_use_case.execute(dto)

        compiler_errors: list[dict[str, str]] = []
        linter_errors: list[dict[str, str]] = []
        pattern_errors: list[dict[str, str]] = []

        for error in check_result.errors:
            item = {"text": error.text, "type": error.error_type}
            if error.error_type == "CONSTRUCTION":
                pattern_errors.append(item)
            elif error.error_type == "COMPILER":
                compiler_errors.append(item)
            else:
                linter_errors.append(item)

        return compiler_errors, linter_errors, pattern_errors

    def _run_test_cases(
        self, task_id: int, code: str, language: str, has_compiler_errors: bool
    ) -> list[dict[str, Any]]:
        from application.tasks.services.catalog.task_catalog_orchestrator import get_task_test_cases

        test_cases = get_task_test_cases(task_id=task_id)
        if not test_cases:
            return []

        if has_compiler_errors:
            return []

        raw_results = self._test_runner.run(
            code=code,
            language=language,
            test_cases=test_cases,
        )
        return [item.to_dict() for item in raw_results]
