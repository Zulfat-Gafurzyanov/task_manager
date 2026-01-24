from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.connection import async_session_maker
from src.repository.tasks.tasks import TaskRepository
from src.service.tasks import TaskService


async def get_session():
    """Dependency для получения сессии БД."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()  # Автокоммит после успешного запроса
        except Exception:
            await session.rollback()
            raise


def get_task_service(
        session: Annotated[AsyncSession, Depends(get_session)]) -> TaskService:
    """Dependency для получения сервисного слоя."""
    repository = TaskRepository(session)
    return TaskService(repository)
