from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.v1 import tasks
from src.db.connection import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # https://fastapi.tiangolo.com/ru/tutorial/sql-databases/#create-database-tables-on-startup
    # Для продакшн вы, вероятно, будете использовать скрипт миграций, который выполняется до запуска приложения. 🤓
    await create_db_and_tables()
    yield

# ??? Нужно ли это убирать в отдельный файл? или эти вещи обычно не пишут?
tags_metadata = [
    {
        "name": "tasks",
        "description": (
            "**Управление задачами**: создание, чтение, обновление и "
            "удаление задач с поддержкой фильтрации и сортировки."
        )
    }
]

app = FastAPI(
    lifespan=lifespan,
    # ??? Нужно ли это убирать в отдельный файл? или эти вещи обычно не пишут?
    openapi_tags=tags_metadata,
    openapi_url="/api/v1/openapi.json",
    redoc_url="/api/v1/redoc",
    docs_url="/api/v1/docs",
    title="Task Manager API",
    description=(
        "**Сервис** для эффективного управления задачами "
        "с расширенными возможностями фильтрации и организации."
    ),
    version="1.0",
    contact={
        "name": "Zulfat Gafurzyanov",
        "url": "https://github.com/Zulfat-Gafurzyanov",
        "telegram": "@Zulfat_Gafurzyanov",
    }
)
app.include_router(tasks.router, prefix="/v1", tags=["tasks"])
