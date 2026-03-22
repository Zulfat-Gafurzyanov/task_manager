import logging
from collections.abc import Callable

from aio_pika import ExchangeType, Message, connect
from aio_pika.abc import AbstractIncomingMessage

from src.core.config import settings

logger = logging.getLogger(__name__)


class RpcConsumer:
    """Потребитель для обработки RPC-запросов."""

    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url

    async def start_consuming(
        self,
        queue_name: str,
        callback: Callable,
        response_exchange_name: str = "response_exchange",
    ):
        connection = await connect(self.amqp_url)
        channel = await connection.channel()
        logger.info(
            "RPC Consumer: начало прослушивания очереди '%s'.", queue_name,
        )
        # обменник + очередь
        response_exchange = await channel.declare_exchange(
            name=response_exchange_name, type=ExchangeType.DIRECT)
        queue = await channel.declare_queue(name=queue_name, auto_delete=False)
        # обработка сообщений
        async with queue.iterator() as iterator:
            message: AbstractIncomingMessage
            async for message in iterator:
                async with message.process(requeue=False):
                    if message.headers:
                        response = await callback(
                            message.body,
                            message.headers
                        )
                    else:
                        response = await callback(message.body)
                    await response_exchange.publish(
                        Message(
                            body=response.encode(),
                            correlation_id=message.correlation_id,
                        ),
                        routing_key=message.reply_to,
                    )


rpc_consumer = RpcConsumer(amqp_url=settings.RABBIT_AMQP)
