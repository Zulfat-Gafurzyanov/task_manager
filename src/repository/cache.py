from redis.asyncio import Redis

STATUS_ALL_KEY = "statuses:all"
USER_KEY = "user:{user_id}"
TOKEN_KEY = "user:{user_id}:token:{jti}"


class CacheRepository:
    """Репозиторий для работы с Redis кешем."""

    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str) -> str | None:
        """Получить из кеша."""
        return await self.redis.get(key)

    async def setex(self, key: str, ttl: int, value: str) -> None:
        """Сохранить в кеш с обязательным TTL."""
        await self.redis.setex(key, ttl, value)

    async def delete(self, key: str) -> None:
        """Удалить из кеша."""
        await self.redis.delete(key)

    async def delete_by_pattern(self, pattern: str) -> None:
        """Удалить все ключи по паттерну."""
        keys = []
        async for key in self.redis.scan_iter(pattern):
            keys.append(key)
        if keys:
            await self.redis.delete(*keys)

    @property
    def key_all_statuses(self) -> str:
        return STATUS_ALL_KEY

    @staticmethod
    def key_user(user_id: int) -> str:
        return USER_KEY.format(user_id=user_id)

    @staticmethod
    def key_token(user_id: int, jti: str) -> str:
        return TOKEN_KEY.format(user_id=user_id, jti=jti)
