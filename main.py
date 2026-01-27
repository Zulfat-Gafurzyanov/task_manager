import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from dotenv import load_dotenv

from src.core.keys import Keys
from src.db.redis import redis_client
from src.api.v1.tasks import router_v1
from src.exseption.handlers import register_exception_handlers

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    # Инициализация ресурсов.
    await redis_client.connect()

    # Инициализация ключей шифрования
    await Keys.initialize(
        private_key_path=os.environ['PRIVATE_KEY_PATH'],
        public_key_path=os.environ['PUBLIC_KEY_PATH'],
        private_key_password=os.environ['PRIVATE_KEY_PASSWORD']
    )

    yield
    # Освобождение ресурсов.
    await redis_client.close()

tags_metadata = [
    {
        "name": "tasks",
        "description": (
            "**Управление задачами**: создание, чтение, обновление и "
            "удаление задач."
        )
    }
]

app = FastAPI(
    lifespan=lifespan,
    openapi_tags=tags_metadata,
    openapi_url="/api/v1/openapi.json",
    redoc_url="/api/v1/redoc",
    docs_url="/api/v1/docs",
    title="Task Manager API",
    description=("**Сервис** для управления вашими задачами."),
    version="1.0",
    contact={
        "name": "Zulfat Gafurzyanov",
        "url": "https://github.com/Zulfat-Gafurzyanov",
        "telegram": "@Zulfat_Gafurzyanov",
    }
)

app.include_router(router_v1, prefix="/api/v1", tags=["tasks"])
register_exception_handlers(app)


@app.get("/", tags=["root"])
def root():
    return {
        "message": "Task Manager API",
        "docs": "/api/v1/docs",
        "redoc": "/api/v1/redoc"
    }

# TODO: config.py
