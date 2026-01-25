import json
from typing import Any

from redis.asyncio import Redis


class CacheRepository:
    """
    Репозиторий для работы с Redis кешем.

    Предоставляет методы для получения, сохранения и удаления данных из кеша.
    Автоматически сериализует/десериализует данные в JSON.
    """
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> Any:
        """Получить из кеша."""
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        """Сохранить в кеш."""
        await self.redis.set(key, json.dumps(value), ex=ttl)

    async def delete(self, key: str) -> None:
        """Удалить из кеша."""
        await self.redis.delete(key)
