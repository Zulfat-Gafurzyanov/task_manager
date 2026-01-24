from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.v1.tasks import router_v1
from src.exseption.handlers import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Выполняет инициализацию ресурсов при старте приложения.

    В текущей реализации создает базу данных таблицы при запуске.
    """
    yield

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
