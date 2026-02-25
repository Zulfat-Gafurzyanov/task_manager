import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from dotenv import load_dotenv

from src.core.keys import Keys
from src.db.redis import redis_client
from src.api.v1.tasks import router_v1 as task_router
from src.api.v1.users import router_v1 as users_router
from src.exception.handlers import register_exception_handlers

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Инициализация редис.
    await redis_client.connect()

    # Инициализация ключей шифрования
    await Keys.initialize(
        private_key_path=os.environ['PRIVATE_KEY_PATH'],
        public_key_path=os.environ['PUBLIC_KEY_PATH'],
        private_key_password=os.environ['PRIVATE_KEY_PASSWORD']
    )

    yield
    await redis_client.close()

tags_metadata = [
    {
        "name": "task",
        "description": (
            "**Управление задачами**: создание, чтение, обновление и "
            "удаление задач."
        )
    },
    {
        "name": "user",
        "description": (
            "**Аутентификация и авторизация**: регистрация, вход, "
            "обновление токенов."
        )
    }
]

app = FastAPI(
    lifespan=lifespan,
    openapi_tags=tags_metadata,
    title="Task Manager API",
    description=("**Сервис** для управления вашими задачами."),
    version="1.0",
    contact={
        "name": "Zulfat Gafurzyanov",
        "url": "https://github.com/Zulfat-Gafurzyanov",
        "telegram": "@Zulfat_Gafurzyanov",
    }
)

app.include_router(task_router, prefix="/api/v1", tags=["task"])
app.include_router(users_router, prefix="/api/v1/auth", tags=["user"])
register_exception_handlers(app)

# TODO: config.py
