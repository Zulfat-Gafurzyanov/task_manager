import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.core.config import settings
from src.core.keys import Keys
from src.db.connection import close_db_pool, init_db_pool
from src.db.redis import redis_client
from src.api.v1.router import v1_router
from src.broker.rpc_publisher import rpc_publisher
from src.exception.handlers import register_exception_handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # ===== Запуск =====

    await Keys.initialize(
        private_key_path=settings.JWT_PRIVATE_KEY_PATH,
        public_key_path=settings.JWT_PUBLIC_KEY_PATH,
        private_key_password=settings.PRIVATE_KEY_PASSWORD
    )
    await init_db_pool()

    try:
        await redis_client.connect()
        logger.info("Redis подключен")
    except Exception as e:
        logger.warning("Redis недоступен: %s", e)

    try:
        await rpc_publisher.connect(
            response_queue_name="task_assignment_response_queue",
            response_exchange_name="response_exchange",
        )
    except Exception as e:
        logger.warning("RabbitMQ недоступен, RPC отключён: %s", e)

    yield

    # ===== Закрытие =====
    await redis_client.close()
    await close_db_pool()
    await rpc_publisher.close()

tags_metadata = [
    {
        "name": "tasks",
        "description": (
            "**Управление задачами**: создание, чтение, обновление и "
            "удаление задач."
        )
    },
    {
        "name": "users",
        "description": (
            "**Аутентификация и авторизация**: регистрация, вход, "
            "обновление токенов."
        )
    },
    {
        "name": "assignments",
        "description": (
            "**Назначение пользователей на задачи**: добавление, удаление и "
            "просмотр исполнителей."
        )
    }
]

app = FastAPI(
    lifespan=lifespan,
    openapi_tags=tags_metadata,
    title=settings.APP_NAME,
    description=("**Сервис** для управления вашими задачами."),
    version="1.0",
    contact={
        "name": "Zulfat Gafurzyanov",
        "url": "https://github.com/Zulfat-Gafurzyanov",
        "telegram": "@Zulfat_Gafurzyanov",
    }
)

app.include_router(v1_router, prefix="/api")

register_exception_handlers(app)
