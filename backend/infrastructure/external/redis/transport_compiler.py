# backend/infrastructure/transports/redis/redis_compiler.py

import json
from typing import AsyncGenerator
from .redis_base import RedisClient

COMPILER_QUEUE = "compiler_queue"


class RedisCompilerQueue:

    async def publish(self, payload: dict):
        client = await RedisClient.get_client()
        await client.rpush(COMPILER_QUEUE, json.dumps(payload))

    async def listen(self) -> AsyncGenerator[dict, None]:
        client = await RedisClient.get_client()

        while True:
            # BLPOP блокирует соединение
            result = await client.blpop(COMPILER_QUEUE)

            if result:
                _, item = result
                yield json.loads(item)
