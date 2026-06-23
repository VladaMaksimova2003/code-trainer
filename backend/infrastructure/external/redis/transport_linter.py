# backend/infrastructure/transports/redis/redis_linter.py

import json
from typing import AsyncGenerator

from .redis_base import RedisClient
from domain.entities.learning.user_solution import UserSolution

LINTER_QUEUE = "linter_queue"


class RedisLinterQueue:

    async def publish(self, solution: UserSolution):
        client = await RedisClient.get_client()

        payload = {
            "code": solution.code,
            "language": solution.language,
            "task_id": solution.task_id,
            "user_id": solution.user_id,
        }

        await client.rpush(LINTER_QUEUE, json.dumps(payload))

    async def listen(self) -> AsyncGenerator[UserSolution, None]:
        client = await RedisClient.get_client()

        while True:
            # Блокирующее ожидание
            result = await client.blpop(LINTER_QUEUE)

            if result:
                _, raw = result
                data = json.loads(raw)

                yield UserSolution(
                    code=data["code"],
                    language=data["language"],
                    task_id=data["task_id"],
                    user_id=data["user_id"],
                )
