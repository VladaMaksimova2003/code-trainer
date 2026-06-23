"""Deprecated in-memory queue — use RedisExecutionQueue."""
from infrastructure.execution.redis_execution_queue import RedisExecutionQueue

ExecutionQueue = RedisExecutionQueue

__all__ = ["ExecutionQueue", "RedisExecutionQueue"]
