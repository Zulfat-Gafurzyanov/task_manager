from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker
)
from sqlmodel import SQLModel


engine = create_async_engine("sqlite+aiosqlite:///database.db")
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


# ???
# Как осуществить абстракцию? У меня все на SQLModel.
async def create_db_and_tables():
    """Создает базу данных и все таблицы."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    """Генератор для получения асинхронной сессии базы данных."""
    async with async_session_maker() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
