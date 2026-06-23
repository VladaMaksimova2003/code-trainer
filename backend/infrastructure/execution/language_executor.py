"""Deprecated — use ExecutionJobService from API, ExecutionCore in workers only."""
from infrastructure.execution.execution_guard import WorkerOnlyExecutionError


def get_language_executor():
    raise WorkerOnlyExecutionError(
        "Direct execution is disabled. Use ExecutionJobService.submit()."
    )
