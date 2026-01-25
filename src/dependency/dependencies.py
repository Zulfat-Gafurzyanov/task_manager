from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.connection import async_session_maker
from src.db.redis import redis_client
from src.repository.cache import CacheRepository
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


def get_task_repository(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> TaskRepository:
    """Dependency для получения репозитория задач."""
    return TaskRepository(session)


def get_cache_repository() -> CacheRepository:
    """Dependency для получения репозитория кеша."""
    redis = redis_client.get_redis()
    return CacheRepository(redis)


def get_task_service(
        task_repo: Annotated[TaskRepository, Depends(get_task_repository)],
        cache_repo: Annotated[CacheRepository, Depends(get_cache_repository)]
) -> TaskService:
    """Dependency для получения сервисного слоя c кешем."""
    return TaskService(task_repo, cache_repo)
