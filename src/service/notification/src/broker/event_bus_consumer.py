import json
import logging

import redis.asyncio as aioredis

logger = logging.getLogger(__name__)


class EventBusConsumer:
    def __init__(self, redis_url: str):
        self.client = aioredis.from_url(redis_url, decode_responses=True)

    async def subscribe(self, handlers: dict):
        pubsub = self.client.pubsub()
        channels = list(handlers.keys())
        await pubsub.subscribe(*channels)
        logger.info(
            "EventBus-notification-serv: подписался на каналы: %s", channels,
        )

        async for message in pubsub.listen():
            if message["type"] == "message":
                channel = message["channel"]
                data = json.loads(message["data"])
                handler = handlers.get(channel)
                if handler:
                    await handler(data)
