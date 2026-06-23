"""Pipeline logic for execution workers (Docker via ExecutionCore)."""
from __future__ import annotations

import re
from contextlib import contextmanager
from typing import Any, Iterator

from sqlalchemy.orm import Session

from application.execution.dto import CheckSolutionDTO
from application.execution.use_cases.check_solution import CheckSolutionUseCase
from application.tasks.services.catalog.task_catalog_orchestrator import (
    get_task_expected_concept_ids,
    get_task_mcq_spec,
    get_task_test_cases,
    is_mcq_task,
    is_snippet_translation_task,
    should_skip_expected_concept_checks,
)
from infrastructure.db.session import SessionLocal
from infrastructure.execution.execution_core import ExecutionCore
from infrastructure.execution.test_case_result import TestCaseResult
from shared.containers import Container


_NON_BLOCKING_WARNING_TYPES = frozenset(
    {"CONSTRUCTION_WARNING", "TRANSFER_PITFALL", "ALGORITHM"}
)


def _is_non_blocking_warning(item: dict[str, str]) -> bool:
    return str(item.get("type") or "").upper() in _NON_BLOCKING_WARNING_TYPES

@contextmanager
def _task_db_session() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class WorkerPipelineRunner:
    """Runs solution checks inside workers only."""

    @staticmethod
    def _looks_like_diagnostic_line(text: str) -> bool:
        line = str(text or "").strip()
        if not line:
            return False
        if "Free Pascal Compiler" in line or "/usr/bin/ppcx" in line:
            return False
        return bool(
            re.match(r"^(Error|Fatal|Warning),?\s*(строка\s+\d+)?:", line, re.I)
            or re.match(r"^(Error|Fatal|Warning):", line, re.I)
            or re.match(r"^Line\s+\d+", line, re.I)
        )

    @staticmethod
    def _parse_diagnostic_lines(texts: list[str]) -> list[str]:
        import re

        from infrastructure.execution.output_parser import parse_diagnostics

        seen: set[str] = set()
        out: list[str] = []
        for raw in texts:
            blob = str(raw or "").strip()
            if not blob:
                continue
            parsed = parse_diagnostics(blob)
            if parsed:
                for msg in parsed:
                    line = str(msg).strip()
                    if line and line not in seen:
                        seen.add(line)
                        out.append(line)
                continue
            if WorkerPipelineRunner._looks_like_diagnostic_line(blob):
                if blob not in seen:
                    seen.add(blob)
                    out.append(blob)
        return out

    @staticmethod
    def _append_diagnostic_errors(
        target: list[dict[str, str]],
        texts: list[str],
        *,
        error_type: str,
    ) -> None:
        existing = {item["text"] for item in target}
        for msg in WorkerPipelineRunner._parse_diagnostic_lines(texts):
            if msg in existing:
                continue
            existing.add(msg)
            target.append({"text": msg, "type": error_type})

    def __init__(self) -> None:
        self._core = ExecutionCore()
        container = Container()
        container.init_resources()
        self._check_use_case: CheckSolutionUseCase = container.check_solution_use_case()

    def run_full(self, task_id: int, code: str, language: str) -> dict[str, Any]:
        """Full check (guest/demo) — same pipeline as submission, including MPLT feedback."""
        return self.run_submission(task_id, code, language)

    def run_submission(self, task_id: int, code: str, language: str) -> dict[str, Any]:
        """Submission path: compile/lint, expected concepts, then test cases."""
        with _task_db_session() as db:
            mcq = get_task_mcq_spec(db=db, task_id=task_id)
            if mcq:
                return self._run_mcq_submission(task_id, code, mcq)

            test_cases = get_task_test_cases(db=db, task_id=task_id)
            lang = str(language).lower()
            executable = self._prepare_code_for_execution(db, task_id, code, language)

            compiler_errors: list[dict[str, str]] = []
            linter_errors: list[dict[str, str]] = []
            if lang == "pascal" and str(executable or "").strip():
                self._append_diagnostic_errors(
                    compiler_errors,
                    self._core.compile_check(lang, executable),
                    error_type="COMPILER",
                )
                if not compiler_errors:
                    self._append_diagnostic_errors(
                        linter_errors,
                        self._core.lint(lang, executable),
                        error_type="LINT",
                    )

            pattern_errors, concept_check = self._run_expected_concept_checks(
                db, task_id, code, language
            )
            pattern_errors = self._append_atcc_carryover_warnings(
                db,
                task_id,
                code,
                language,
                pattern_errors,
            )

            if (
                not pattern_errors
                and not test_cases
                and is_snippet_translation_task(db, task_id)
            ):
                legacy_compiler, legacy_linter, legacy_patterns = self._run_legacy_checks(
                    db, task_id, code, language, mode="pattern_only"
                )
                pattern_errors = legacy_patterns
                if not compiler_errors:
                    compiler_errors = legacy_compiler
                if not linter_errors:
                    linter_errors = legacy_linter

            test_results: list[dict[str, Any]] = []
            blocking_pattern_errors = [
                item
                for item in pattern_errors
                if not _is_non_blocking_warning(item)
            ]
            if test_cases and not blocking_pattern_errors and not compiler_errors:
                test_results = self._run_test_cases(
                    db=db,
                    task_id=task_id,
                    code=code,
                    language=language,
                    has_compiler_errors=False,
                )
                for item in test_results:
                    if item.get("status") == "ERROR" and item.get("message"):
                        if compiler_errors:
                            continue
                        self._append_diagnostic_errors(
                            compiler_errors,
                            [str(item["message"])],
                            error_type="COMPILER",
                        )
                        break
                tests_failed = any(
                    str(item.get("status") or "").upper() != "PASSED"
                    for item in test_results
                )
                if tests_failed:
                    pattern_errors = self._append_post_submit_feedback(
                        db,
                        task_id,
                        code,
                        language,
                        pattern_errors,
                        test_results,
                    )
            elif compiler_errors and not blocking_pattern_errors:
                synthetic_results = [
                    {
                        "case": 1,
                        "status": "ERROR",
                        "message": compiler_errors[0].get("text", ""),
                    }
                ]
                pattern_errors = self._append_post_submit_feedback(
                    db,
                    task_id,
                    code,
                    language,
                    pattern_errors,
                    synthetic_results,
                )

        return self._build_result(
            task_id,
            compiler_errors,
            linter_errors,
            pattern_errors,
            test_results,
            require_tests=bool(test_cases),
            concept_check=concept_check,
        )

    @staticmethod
    def _normalize_mcq_answer(text: str) -> str:
        return "\n".join(line.rstrip() for line in str(text or "").replace("\r\n", "\n").splitlines()).strip()

    def _run_mcq_submission(
        self,
        task_id: int,
        code: str,
        mcq: dict[str, Any],
    ) -> dict[str, Any]:
        options: list[str] = list(mcq.get("options") or [])
        correct_index = int(mcq.get("correct_index", 0))
        if not options or correct_index < 0 or correct_index >= len(options):
            return WorkerPipelineRunner._build_result(task_id, [], [], [], [])

        selected = self._normalize_mcq_answer(code)
        correct = self._normalize_mcq_answer(options[correct_index])
        explanation = str(mcq.get("explanation") or "").strip()

        if selected == correct:
            test_results = [
                {
                    "case": 1,
                    "status": "PASSED",
                    "inputs": "",
                    "expected": "correct",
                    "actual": "correct",
                    "message": explanation or "Верный ответ",
                    "duration_ms": 0,
                }
            ]
            return self._build_result(task_id, [], [], [], test_results, require_tests=True)

        test_results = [
            {
                "case": 1,
                "status": "FAILED",
                "inputs": "",
                "expected": "correct",
                "actual": "incorrect",
                "message": explanation or "Неверный вариант ответа",
                "duration_ms": 0,
            }
        ]
        return self._build_result(task_id, [], [], [], test_results, require_tests=True)

    @staticmethod
    def _build_result(
        task_id: int,
        compiler_errors: list[dict[str, str]],
        linter_errors: list[dict[str, str]],
        pattern_errors: list[dict[str, str]],
        test_results: list[dict[str, Any]],
        *,
        require_tests: bool = False,
        concept_check: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        tests_passed = bool(test_results) and all(
            item["status"] == "PASSED" for item in test_results
        )
        concept_passed = True
        if concept_check and concept_check.get("enabled"):
            concept_passed = bool(concept_check.get("passed"))

        if (
            tests_passed
            and concept_check
            and concept_check.get("enabled")
            and not concept_passed
        ):
            from application.curriculum.validation.expected_concept_checker import (
                format_construction_warning_messages,
            )

            summary_messages = format_construction_warning_messages(
                concept_check,
                tests_passed=True,
            )
            if summary_messages:
                pattern_errors = [
                    item
                    for item in pattern_errors
                    if str(item.get("type") or "").upper() != "CONSTRUCTION_WARNING"
                ]
                pattern_errors = [*summary_messages, *pattern_errors]

        blocking_pattern_errors = [
            item
            for item in pattern_errors
            if not _is_non_blocking_warning(item)
        ]
        success = (
            not compiler_errors
            and not blocking_pattern_errors
            and (tests_passed if require_tests else True)
            and concept_passed
        )
        payload: dict[str, Any] = {
            "task_id": task_id,
            "success": success,
            "compiler_errors": compiler_errors,
            "linter_errors": linter_errors,
            "pattern_errors": pattern_errors,
            "test_results": test_results,
        }
        if concept_check is not None:
            payload["concept_check"] = concept_check
        return payload

    def _run_expected_concept_checks(
        self,
        db: Session,
        task_id: int,
        code: str,
        language: str,
    ) -> tuple[list[dict[str, str]], dict[str, Any] | None]:
        lang = self._resolve_concept_check_language(code, language)
        if lang not in {"pascal", "python", "cpp", "java", "csharp"}:
            return [], None
        if should_skip_expected_concept_checks(db=db, task_id=task_id):
            return [], None
        concept_ids = get_task_expected_concept_ids(db=db, task_id=task_id, language=lang)
        if not concept_ids:
            return [], None
        from application.curriculum.validation.expected_concept_checker import (
            check_expected_concepts,
        )

        check = check_expected_concepts(code, lang, concept_ids)
        concept_check = check.to_dict()
        return [], concept_check

    @staticmethod
    def _resolve_concept_check_language(code: str, language: str) -> str:
        """Pick checker profile from code syntax (learning language wins over task default)."""
        import re

        text = str(code or "")
        lowered = text.lower()

        if re.search(
            r"\bprint\s*\(|\bint\s*\(\s*input|for\s+_?\w*\s+in\s+range|#\s*[^\n]",
            lowered,
        ) and not re.search(r"\b(begin|writeln|program)\b", lowered):
            return "python"
        if re.search(r"\bConsole\.Write(Line)?\b", text):
            return "csharp"
        if re.search(r"\bstd::\w+|#include\b", text):
            return "cpp"
        if re.search(r"\bSystem\.out\.|public\s+static\s+void\s+main\b", text):
            return "java"
        if re.search(r"\b(begin|writeln|program)\b", lowered):
            return "pascal"

        lang = str(language or "pascal").strip().lower()
        if lang == "python" and re.search(r"\b(begin|writeln|program)\b", lowered):
            return "pascal"
        if lang == "pascal" and re.search(r"\bprint\s*\(", lowered) and not re.search(
            r"\bbegin\b", lowered
        ):
            return "python"
        return lang

    @staticmethod
    def _merge_pattern_feedback(
        pattern_errors: list[dict[str, str]],
        extra: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        if not extra:
            return pattern_errors
        existing = {str(item.get("text") or "") for item in pattern_errors}
        merged = list(pattern_errors)
        for item in extra:
            text = str(item.get("text") or "")
            if text and text not in existing:
                merged.append(item)
                existing.add(text)
        return merged

    def _append_atcc_carryover_warnings(
        self,
        db: Session,
        task_id: int,
        code: str,
        language: str,
        pattern_errors: list[dict[str, str]],
    ) -> list[dict[str, str]]:
        from application.curriculum.display.atcc_idiom_engine import detect_atcc_carryover
        from application.curriculum.display.mplt_submit_profile import resolve_mplt_submit_profile
        from application.curriculum.display.pitfall_catalog import get_pitfall

        profile = resolve_mplt_submit_profile(
            db,
            task_id,
            submission_language=language,
        )
        if not profile or not profile.pitfall_ids:
            return pattern_errors
        if not any(
            str(get_pitfall(str(pid)).get("transfer_type") or "").upper() == "ATCC"
            for pid in profile.pitfall_ids
            if get_pitfall(str(pid))
        ):
            return pattern_errors

        atcc_warnings = detect_atcc_carryover(
            profile.source_language,
            profile.target_language,
            code,
            expected_concepts=profile.pitfall_concept_ids,
        )
        if not atcc_warnings:
            return pattern_errors

        pitfall_id = profile.dominant_pitfall_id
        enriched = []
        for item in atcc_warnings:
            row = dict(item)
            row.setdefault("pitfall_id", pitfall_id)
            enriched.append(row)
        return self._merge_pattern_feedback(pattern_errors, enriched)

    def _append_post_submit_feedback(
        self,
        db: Session,
        task_id: int,
        code: str,
        language: str,
        pattern_errors: list[dict[str, str]],
        test_results: list[dict[str, Any]],
    ) -> list[dict[str, str]]:
        from application.curriculum.display.algorithm_debug_detector import (
            detect_algorithm_debug,
        )
        from application.curriculum.display.mplt_submit_profile import resolve_mplt_submit_profile
        from application.curriculum.display.transfer_pitfall_detector import (
            detect_transfer_pitfalls,
        )

        profile = resolve_mplt_submit_profile(
            db,
            task_id,
            submission_language=language,
        )
        if not profile:
            return pattern_errors

        merged = pattern_errors

        if profile.debug_id:
            algo_feedback = detect_algorithm_debug(
                debug_id=profile.debug_id,
                target_language=profile.target_language,
                code=code,
                test_results=test_results,
                buggy_code=profile.buggy_code,
            )
            merged = self._merge_pattern_feedback(merged, algo_feedback)

        if profile.pitfall_ids:
            from application.curriculum.display.pitfall_catalog import get_pitfall

            atcc_warnings = [
                item
                for item in merged
                if str(item.get("type") or "").upper() == "TRANSFER_PITFALL"
                and str(item.get("transfer_type") or "").upper() == "ATCC"
            ]
            for pitfall_id in profile.pitfall_ids:
                spec = get_pitfall(str(pitfall_id))
                if not spec:
                    continue
                transfer_type = str(spec.get("transfer_type") or "").upper()
                transfer_feedback = detect_transfer_pitfalls(
                    pitfall_id=str(pitfall_id),
                    transfer_type=transfer_type,
                    source_language=profile.source_language,
                    target_language=profile.target_language,
                    code=code,
                    test_results=test_results,
                    buggy_code=profile.buggy_code,
                    atcc_warnings=atcc_warnings,
                )
                merged = self._merge_pattern_feedback(merged, transfer_feedback)

        if any(str(item.get("type") or "").upper() == "TRANSFER_PITFALL" for item in merged):
            merged = [
                item
                for item in merged
                if str(item.get("type") or "").upper()
                not in {"CONSTRUCTION_WARNING", "ALGORITHM"}
            ]

        return merged

    def _append_transfer_pitfall_warnings(
        self,
        db: Session,
        task_id: int,
        code: str,
        language: str,
        pattern_errors: list[dict[str, str]],
        test_results: list[dict[str, Any]],
    ) -> list[dict[str, str]]:
        return self._append_post_submit_feedback(
            db,
            task_id,
            code,
            language,
            pattern_errors,
            test_results,
        )

    def _run_legacy_checks(
        self,
        db: Session,
        task_id: int,
        code: str,
        language: str,
        mode: str,
    ) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
        from application.tasks.services.catalog.task_catalog_orchestrator import (
            get_task_constructions,
        )

        dto = CheckSolutionDTO(
            code=code,
            language=language,
            constructions=get_task_constructions(db=db, task_id=task_id),
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

    def run_lint_only(self, task_id: int, code: str, language: str) -> dict[str, Any]:
        with _task_db_session() as db:
            if is_mcq_task(db=db, task_id=task_id):
                return {"task_id": task_id, "linter_errors": []}
            executable = self._prepare_code_for_execution(db, task_id, code, language)
            if not str(executable or "").strip():
                return {"task_id": task_id, "linter_errors": []}
            linter_errors: list[dict[str, str]] = []
            self._append_diagnostic_errors(
                linter_errors,
                self._core.lint(str(language).lower(), executable),
                error_type="LINT",
            )
        return {"task_id": task_id, "linter_errors": linter_errors}

    def run_pattern_only(self, task_id: int, code: str, language: str) -> dict[str, Any]:
        with _task_db_session() as db:
            _, _, pattern_errors = self._run_checks(
                db, task_id, code, language, mode="pattern_only"
            )
        return {"task_id": task_id, "pattern_errors": pattern_errors}

    def _run_checks(
        self,
        db: Session,
        task_id: int,
        code: str,
        language: str,
        mode: str,
    ) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
        if mode == "lint_only":
            executable = self._prepare_code_for_execution(db, task_id, code, language)
            linter_errors: list[dict[str, str]] = []
            if str(executable or "").strip():
                self._append_diagnostic_errors(
                    linter_errors,
                    self._core.lint(str(language).lower(), executable),
                    error_type="LINT",
                )
            return [], linter_errors, []

        pattern_errors, _concept_check = self._run_expected_concept_checks(db, task_id, code, language)
        if pattern_errors:
            return [], [], pattern_errors
        return self._run_legacy_checks(db, task_id, code, language, mode)

    def _run_test_cases(
        self,
        db: Session,
        task_id: int,
        code: str,
        language: str,
        has_compiler_errors: bool,
    ) -> list[dict[str, Any]]:
        test_cases = get_task_test_cases(db=db, task_id=task_id)
        if not test_cases or has_compiler_errors:
            return []

        executable_code = self._prepare_code_for_execution(
            db, task_id, code, language
        )
        raw = self._core.run_tests(str(language).lower(), executable_code, test_cases)
        return [self._to_dict(item) for item in raw]

    @staticmethod
    def _prepare_code_for_execution(
        db: Session,
        task_id: int,
        code: str,
        language: str,
    ) -> str:
        if str(language).lower() != "pascal":
            return code
        import re

        if not re.search(r"\bprogram\b", code, re.I):
            from application.curriculum.pascal.catalog.pascal_v311_test_case_resolver import (
                wrap_pascal_program_body,
                wrap_pascal_snippet,
            )

            if is_snippet_translation_task(db, task_id):
                return wrap_pascal_snippet(code)
            return wrap_pascal_program_body(code)
        return code

    @staticmethod
    def _to_dict(item: TestCaseResult) -> dict[str, Any]:
        return {
            "case": item.case,
            "status": item.status,
            "inputs": item.inputs,
            "expected": item.expected,
            "actual": item.actual,
            "message": item.message,
            "duration_ms": item.duration_ms,
        }
