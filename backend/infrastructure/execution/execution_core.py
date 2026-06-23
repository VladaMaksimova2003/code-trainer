"""Docker execution core — callable only inside execution workers."""
from __future__ import annotations

import os

from domain.entities.language import LanguageConfig, LanguageFeature
from infrastructure.execution.docker_executor import DockerExecutor
from infrastructure.execution.execution_guard import assert_worker_context
from infrastructure.execution.language_registry import language_registry
from infrastructure.execution.test_case_result import TestCaseResult
from infrastructure.execution.test_strategies import get_test_strategy


class ExecutionCore:
    """Direct Docker runner used by execution workers."""

    def __init__(self, docker: DockerExecutor | None = None) -> None:
        self._docker = docker or DockerExecutor()

    def get_config(self, language_id: str) -> LanguageConfig:
        return language_registry.get_or_raise(language_id)

    def lint(self, language_id: str, code: str) -> list[str]:
        assert_worker_context()
        cfg = self.get_config(language_id)
        if not cfg.supports(LanguageFeature.LINT):
            return []
        return self._run_mode(cfg, code, "lint")

    def compile_check(self, language_id: str, code: str) -> list[str]:
        assert_worker_context()
        cfg = self.get_config(language_id)
        if not cfg.supports(LanguageFeature.COMPILE):
            return []
        return self._run_mode(cfg, code, "compile")

    def run_tests(
        self,
        language_id: str,
        code: str,
        test_cases: list[dict],
    ) -> list[TestCaseResult]:
        assert_worker_context()
        cfg = self.get_config(language_id)
        if not cfg.supports(LanguageFeature.TEST):
            return get_test_strategy("unsupported", self._docker).run(
                cfg, code, test_cases
            )
        strategy = get_test_strategy(cfg.test.strategy, self._docker)
        return strategy.run(cfg, code, test_cases)

    def _run_mode(self, cfg: LanguageConfig, code: str, mode: str) -> list[str]:
        if not self._docker.is_available():
            raise RuntimeError("Docker is required for code execution")
        if not cfg.docker:
            raise RuntimeError(f"Docker config missing for language '{cfg.id}'")

        if mode == "lint":
            command = cfg.docker.lint
            if not command or not cfg.docker.image:
                return []
            lint_timeout = int(os.getenv("EXECUTION_LINT_TIMEOUT", "5"))
            return self._docker.run_diagnostics(
                cfg.docker.image,
                command,
                code,
                cfg.file_extension,
                timeout=lint_timeout,
            )

        command = cfg.docker.compile or cfg.docker.run
        if not command or not cfg.docker.image:
            return []
        return self._docker.run_diagnostics(
            cfg.docker.image,
            command,
            code,
            cfg.file_extension,
        )
