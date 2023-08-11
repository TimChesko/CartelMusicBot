from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker


class DatabaseManager:

    @staticmethod
    async def create_engine(config):
        postgres = config.postgres
        uri = f"postgresql+asyncpg://{postgres.user}:{postgres.password}@{postgres.host}/{postgres.database}"
        return create_async_engine(uri, echo=False)

    @staticmethod
    async def create_session_maker(engine):
        return async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
