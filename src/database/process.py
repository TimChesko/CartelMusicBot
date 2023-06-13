from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from src.models.tables import Base


class DatabaseManager:

    @asynccontextmanager
    async def create_session(engine):
        async with sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession) as session:
            yield session

    @staticmethod
    async def create_tables(engine):
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


class DatabaseEngine:

    @staticmethod
    async def connect(config):
        uri = f"postgresql+asyncpg://{config.PG_USER}:{config.PG_PASSWORD}@{config.PG_HOST}/{config.PG_DATABASE}"
        return create_async_engine(uri, echo=False)
