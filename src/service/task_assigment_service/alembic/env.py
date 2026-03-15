import asyncio

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from src.core.config import settings
from src.db.models import Base
from src.db.models import *  # noqa: F401, F403 / все модели для Base.metadata

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Миграции без реального подключения к базе данных."""
    context.configure(
        url=settings.DATABASE_URL_SQLALCHEMY,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Миграции с подключением к базе данных."""
    engine = create_async_engine(settings.DATABASE_URL_SQLALCHEMY)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
