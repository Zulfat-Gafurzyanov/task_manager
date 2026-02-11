import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
    AsyncSession
)

load_dotenv()

engine = create_async_engine(
    os.environ['DATABASE_URL'],
    echo=True,  # Убрать в prod.
    pool_pre_ping=True,
    )
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# TODO: настройки для prod
