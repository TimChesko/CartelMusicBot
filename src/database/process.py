from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker

from src.models.tables import Base


class DatabaseManager:

    @staticmethod
    async def connect(config):
        uri = f"postgresql+asyncpg://{config.PG_USER}:{config.PG_PASSWORD}@{config.PG_HOST}/{config.PG_DATABASE}"
        return create_async_engine(uri, echo=False)

    @staticmethod
    @asynccontextmanager
    async def create_session(engine):
        async_session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            yield session

    @staticmethod
    async def create_tables(engine):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
