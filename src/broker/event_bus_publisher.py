import json
import logging

from src.db.redis import RedisClient, redis_client

logger = logging.getLogger(__name__)


class EventBusPublisher:
    def __init__(self, redis: RedisClient):
        self.redis = redis

    async def publish(self, channel: str, payload: dict):
        await self.redis.get_redis().publish(channel, json.dumps(payload))
        logger.debug(
            f"EventBus: опубликовал в канал: <{channel}> данные: {payload}")


event_bus = EventBusPublisher(redis_client)
