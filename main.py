from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.v1 import tasks
from src.db.connection import create_db_and_tables
from src.db.models import Task


@asynccontextmanager
async def lifespan(app: FastAPI):
    # https://fastapi.tiangolo.com/ru/tutorial/sql-databases/#create-database-tables-on-startup
    # Для продакшн вы, вероятно, будете использовать скрипт миграций, который выполняется до запуска приложения. 🤓
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(tasks.router, prefix="/v1", tags=["tasks"])
