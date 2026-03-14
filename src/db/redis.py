
from redis.asyncio import Redis

from src.core.config import settings


class RedisClient:
    """Клиент для работы с Redis."""
    def __init__(self) -> None:
        self.redis: Redis | None = None

    async def connect(self) -> None:
        self.redis = await Redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=10
        )

    async def close(self) -> None:
        if self.redis:
            await self.redis.close()

    def get_redis(self) -> Redis:
        if self.redis is None:
            raise RuntimeError("Redis еще не запустился.")
        return self.redis


redis_client = RedisClient()
