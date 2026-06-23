# backend/infrastructure/transports/redis/redis_base.py

from redis.asyncio import Redis

REDIS_URL = "redis://localhost:6379"


class RedisClient:
    _client: Redis | None = None

    @classmethod
    async def get_client(cls) -> Redis:
        if cls._client is None:
            cls._client = Redis.from_url(REDIS_URL, decode_responses=True)
        return cls._client

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.close()
            cls._client = None
