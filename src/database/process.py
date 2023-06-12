from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker


class AsyncDatabaseManager:
    def __init__(self,
                 engine: AsyncEngine,
                 logger):
        self.engine = engine
        self.logger = logger

    @asynccontextmanager
    async def create_session(self):
        async_session = sessionmaker(bind=self.engine, expire_on_commit=False, class_=AsyncSession)
        async with async_session() as session:
            yield session

    # async def create_tables(self):
    #     async with self.engine.begin() as conn:
    #         await conn.run_sync(Base.metadata.create_all)
    #         self.logger.debug("Created tables")

    async def add(self, query):
        async with self.create_session() as session:
            session.add(query)
            await session.commit()

    async def update(self, query):
        async with self.create_session() as session:
            await session.execute(query)
            await session.commit()

    async def get_row(self, query):
        async with self.create_session() as session:
            return (await session.execute(query)).scalars().first()

    async def get_all(self, query):
        async with self.create_session() as session:
            return (await session.execute(query)).scalars().all()


class DatabaseEngine:

    @staticmethod
    async def connect(config):
        uri = f"postgresql+asyncpg://{config.PG_USER}:{config.PG_PASSWORD}@{config.PG_HOST}/{config.PG_DATABASE}"
        return create_async_engine(uri, echo=False)

    @staticmethod
    async def close_connection(pool) -> None:
        await pool.close()
