# backend/infrastructure/handlers/linter_worker.py

import asyncio
from infrastructure.external.redis.redis_linter import RedisLinterQueue
from application.services.linter_service import LinterServiceInterface
from domain.entities.learning.user_solution import UserSolution


class LinterWorker:

    def __init__(
        self,
        queue: RedisLinterQueue,
        service: LinterServiceInterface,
        max_parallel: int = 5,
    ):
        self._queue = queue
        self._service = service
        self._semaphore = asyncio.Semaphore(max_parallel)

    async def _handle_solution(self, solution: UserSolution):
        async with self._semaphore:
            try:
                await self._service.lint(solution)
            except Exception as exc:
                # тут можно сделать retry / логирование
                print(f"[LinterWorker] Error: {exc}")

    async def start(self):
        async for solution in self._queue.listen():
            asyncio.create_task(self._handle_solution(solution))
