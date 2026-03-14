import asyncio
import logging
import uuid
from typing import Self

from aio_pika import ExchangeType, Message, connect
from aio_pika.abc import AbstractChannel, AbstractConnection, AbstractIncomingMessage, AbstractQueue

from src.core.config import settings


class RpcPublisher:
    connection: AbstractConnection
    channel: AbstractChannel
    response_queue: AbstractQueue

    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self.futures: dict[str, asyncio.Future] = {}

    async def connect(self, response_queue_name: str, response_exchange_name: str) -> Self:
        self.connection = await connect(self.amqp_url)
        # канал + обменник
        self.channel = await self.connection.channel()
        response_exchange = await self.channel.declare_exchange(name=response_exchange_name, type=ExchangeType.DIRECT)
        # очередь
        self.response_queue = await self.channel.declare_queue(name=response_queue_name, exclusive=True)
        await self.response_queue.bind(exchange=response_exchange)
        await self.response_queue.consume(self.on_response, no_ack=True)
        logging.info("Starting consuming from queue: '%s'.", self.response_queue.name)
        return self

    async def on_response(self, message: AbstractIncomingMessage) -> None:
        future: asyncio.Future = self.futures.pop(message.correlation_id)
        future.set_result(message.body)

    async def call(self, message: str, request_queue_name: str, headers: dict | None = None) -> str:
        correlation_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        self.futures[correlation_id] = future
        await self.channel.default_exchange.publish(
            Message(
                message.encode(),
                content_type="application/json",
                correlation_id=correlation_id,
                reply_to=self.response_queue.name,
                headers=headers,
            ),
            routing_key=request_queue_name,
        )
        result = await future
        return result

    async def close(self) -> None:
        if self.connection:
            await self.connection.close()
            logging.critical("Stopping consuming from queue: '%s'.", self.response_queue.name)


rpc_publisher = RpcPublisher(amqp_url=settings.RABBIT_AMQP)
