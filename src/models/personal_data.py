from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError

from src.database.process import DatabaseManager
from src.models.tables import PersonalData


class PersonalDataHandler:

    def __init__(self, engine, logger):
        self.engine = engine
        self.logger = logger

    async def check_all_data_complete(self, tg_id: int) -> bool:

        """
        Проверяет, что значения all_user_data и all_cash_data у пользователя с указанным tg_id равны True.

        :param tg_id: ID пользователя в Telegram.
        :return: True, если значения all_user_data и all_cash_data равны True. False в противном случае или если пользователь не найден.
        """
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(PersonalData).where(and_(PersonalData.tg_id == tg_id))
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                if user:
                    return user.all_user_data and user.all_cash_data
                else:
                    self.logger.error(f"Пользователь с tg_id {tg_id} не найден")
                    return False
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return False


