"""Deprecated RPC queue — use JobStore + ExecutionJobService instead."""
from infrastructure.execution.job_store import JobStore

RedisExecutionQueue = JobStore

__all__ = ["JobStore", "RedisExecutionQueue"]
