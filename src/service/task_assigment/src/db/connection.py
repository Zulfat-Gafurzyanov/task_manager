import logging

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from task_assigment.src.core.config import settings

logger = logging.getLogger(__name__)

engine: AsyncEngine | None = None
async_session_factory: async_sessionmaker[AsyncSession] | None = None


async def init_db_pool() -> None:
    global engine, async_session_factory
    engine = create_async_engine(
        settings.DATABASE_URL_SQLALCHEMY,
        pool_size=settings.DB_MIN_POOL_SIZE,
        max_overflow=settings.DB_MAX_POOL_SIZE - settings.DB_MIN_POOL_SIZE,
        echo=False,
    )
    async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
    logger.info(
        "SQLAlchemy async engine создан (pool_size=%d, max_overflow=%d)",
        settings.DB_MIN_POOL_SIZE,
        settings.DB_MAX_POOL_SIZE - settings.DB_MIN_POOL_SIZE,
    )


async def close_db_pool() -> None:
    global engine
    if engine:
        await engine.dispose()
        engine = None
        logger.info("SQLAlchemy async engine закрыт")
