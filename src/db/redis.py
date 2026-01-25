import os

from dotenv import load_dotenv
from redis.asyncio import Redis

load_dotenv()


class RedisClient:
    """Клиент для управления подключением к Redis."""
    def __init__(self) -> None:
        self.redis: Redis | None = None

    async def connect(self) -> None:
        """Установить соединение с Redis."""
        self.redis = await Redis.from_url(
            os.environ['REDIS_URL'],
            encoding="utf-8",
            decode_responses=True
        )

    async def close(self) -> None:
        """Закрыть соединение с Redis."""
        if self.redis:
            await self.redis.close()

    def get_redis(self) -> Redis:
        """Получить Redis."""
        if self.redis is None:
            raise RuntimeError("Redis еще не запустился.")
        return self.redis


redis_client = RedisClient()
