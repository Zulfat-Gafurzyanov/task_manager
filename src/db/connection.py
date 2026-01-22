import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.db.models import Base

load_dotenv()

engine = create_async_engine(os.environ['DATABASE_URL'])
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_db_and_tables():
    """Создает базу данных и все таблицы."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

        # TODO:
        # создать статусы при инициализации или через админ-зону?
