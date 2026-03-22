import json
import logging

from src.db.redis import RedisClient, redis_client

logger = logging.getLogger(__name__)


class EventBusConsumer:
    def __init__(self, redis: RedisClient):
        self.redis = redis

    async def subscribe(self, handlers: dict):
        pubsub = self.redis.get_redis().pubsub()
        channels = list(handlers.keys())
        await pubsub.subscribe(*channels)
        logger.debug("EventBus: подписался на каналы: %s", channels)

        async for message in pubsub.listen():
            if message["type"] == "message":
                channel = message["channel"]
                data = json.loads(message["data"])
                handler = handlers.get(channel)
                if handler:
                    await handler(data)


event_bus_consumer = EventBusConsumer(redis_client)
