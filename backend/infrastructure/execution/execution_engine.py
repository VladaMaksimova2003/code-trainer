"""Deprecated: API must use ExecutionJobService (async). Workers use ExecutionCore."""
from __future__ import annotations


class ExecutionEngineError(RuntimeError):
    pass


class ExecutionEngine:
    def lint(self, *_args, **_kwargs):
        raise ExecutionEngineError(
            "Sync execution removed. Use POST /solutions/submit and GET /solutions/result/{job_id}"
        )

    def compile_check(self, *_args, **_kwargs):
        raise ExecutionEngineError(
            "Sync execution removed. Use async job API."
        )

    def run_tests(self, *_args, **_kwargs):
        raise ExecutionEngineError(
            "Sync execution removed. Use async job API."
        )


def get_execution_engine(_user_key: str | None = None) -> ExecutionEngine:
    return ExecutionEngine()
