from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

import src.db.connection as db_connection
from src.db.redis import redis_client
from src.repository.cache import CacheRepository
from src.repository.tasks.tasks import TaskRepository
from src.repository.users.users import UserRepository
from src.service.tasks import TaskService
from src.service.users import UserService


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency для получения сессии БД."""
    assert db_connection.async_session_factory is not None, "БД не запущена"
    async with db_connection.async_session_factory() as session:
        yield session


async def get_user_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Отдельная сессия для user_repo."""
    assert db_connection.async_session_factory is not None, "БД не запущена"
    async with db_connection.async_session_factory() as session:
        yield session


def get_task_repository(
        session: Annotated[AsyncSession, Depends(get_session)]
) -> TaskRepository:
    """Dependency для получения репозитория задач."""
    return TaskRepository(session)


def get_user_repository(
        session: Annotated[AsyncSession, Depends(get_user_session)]
) -> UserRepository:
    """Dependency для получения репозитория пользователей."""
    return UserRepository(session)


def get_cache_repository() -> CacheRepository:
    """Dependency для получения репозитория кеша."""
    redis = redis_client.get_redis()
    return CacheRepository(redis)


def get_task_service(
        task_repo: Annotated[TaskRepository, Depends(get_task_repository)],
        cache_repo: Annotated[CacheRepository, Depends(get_cache_repository)]
) -> TaskService:
    """Dependency для получения сервисного слоя задач с кешем."""
    return TaskService(task_repo, cache_repo)


def get_user_service(
        user_repo: Annotated[UserRepository, Depends(get_user_repository)]
) -> UserService:
    """Dependency для получения сервисного слоя пользователей."""
    return UserService(user_repo)
