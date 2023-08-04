from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.models.tables import TrackInfo, PersonalData, PersonalDataTemplate


class DatabaseQueries:

    def __init__(self, session_maker, logger):
        self.session_maker = session_maker
        self.logger = logger

    async def get_docs_by_filters(self, table: str, status: str) -> list | None:
        async with self.session_maker() as session:
            template = {"process": 1, "reject": 2, "approve": 3}
            match table:
                case "personal_data":
                    table = PersonalData
                    if status in template:
                        status = template[status]
                    else:
                        raise ValueError(f"Неверный ключ: {status}. "
                                         f"Возможные ключи: {template.keys()}.")
                case "track_info":
                    table = TrackInfo
                case _:
                    return None
            try:
                query = select(table).where(table.status == status)
                result = await session.execute(query)
                return result.scalars().all()
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return None
