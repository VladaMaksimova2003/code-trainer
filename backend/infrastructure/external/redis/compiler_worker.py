# backend/infrastructure/handlers/compiler_worker.py

import asyncio
from shared.interfaces.services import CompilerServiceInterface
from infrastructure.external.redis.redis_compiler import RedisCompilerQueue


class CompilerWorker:

    def __init__(
        self,
        queue: RedisCompilerQueue,
        compiler_service: CompilerServiceInterface,
        max_parallel: int = 3,
    ):
        self._queue = queue
        self._service = compiler_service
        self._semaphore = asyncio.Semaphore(max_parallel)

    async def _handle(self, data: dict):
        async with self._semaphore:
            await self._service.compile(data)

    async def start(self):
        async for message in self._queue.listen():
            asyncio.create_task(self._handle(message))
