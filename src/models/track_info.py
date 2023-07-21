from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.models.tables import TrackInfo


class TrackInfoHandler:

    def __init__(self, session_maker, logger):
        self.session_maker = session_maker
        self.logger = logger

    async def get_docs_by_status(self, status: str) -> list | None:
        async with self.session_maker() as session:
            try:
                query = select(TrackInfo).where(TrackInfo.status == status)
                result = await session.execute(query)
                docs = result.scalars().all()
                return docs
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return None
