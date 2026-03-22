import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.broker.event_bus_consumer import EventBusConsumer
from src.core.config import settings
from src.handlers.tasks import HANDLERS
from src.ws.router import ws_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    consumer = EventBusConsumer(redis_url=settings.REDIS_URL)
    task = asyncio.create_task(consumer.subscribe(HANDLERS))
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)

app.include_router(ws_router)
