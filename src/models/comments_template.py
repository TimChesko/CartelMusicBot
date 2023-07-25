import sqlalchemy
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.models.tables import CommentsTemplate


class CommentsTemplateHandler:

    def __init__(self, session_maker, logger):
        self.session_maker = session_maker
        self.logger = logger

    @staticmethod
    async def to_dict(obj):
        return {c.key: getattr(obj, c.key) for c in sqlalchemy.inspect(obj).mapper.column_attrs}

    async def get_all_txt_template(self) -> list | None:
        async with self.session_maker() as session:
            try:
                query = select(CommentsTemplate).where(CommentsTemplate.is_text == True)
                result = await session.execute(query)
                return [await self.to_dict(doc) for doc in result.scalars().all()]
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return None
