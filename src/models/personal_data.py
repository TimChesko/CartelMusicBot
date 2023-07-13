import datetime

from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError

from src.database.process import DatabaseManager
from src.models.tables import PersonalData


class PersonalDataHandler:

    def __init__(self, engine, logger):
        self.engine = engine
        self.logger = logger

    async def get_all_data_status(self, tg_id: int) -> tuple[int, int]:

        """
        Проверяет, что значения all_user_data и all_cash_data у пользователя с указанным tg_id равны True.

        :param tg_id: ID пользователя в Telegram.
        :return: bool, bool - all_user_data, all_cash_data
        """

        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(PersonalData).where(and_(PersonalData.tg_id == tg_id))
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                if user:
                    return user.all_passport_data, user.all_bank_data
                else:
                    self.logger.error(f"Пользователь с tg_id {tg_id} не найден")
                    return 0, 0
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return 0, 0

    async def get_personal_data_confirm(self, tg_id: int) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(PersonalData).where(and_(PersonalData.tg_id == tg_id))
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                if user:
                    return user.confirm_use_personal_data
                else:
                    self.logger.error(f"Пользователь с tg_id {tg_id} не найден")
                    return False
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return False

    async def confirm_personal_data(self, tg_id: int) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                user = await session.get(PersonalData, tg_id)
                if user:
                    user.confirm_use_personal_data = True
                    await session.commit()
                    return True
                else:
                    self.logger.error(f"Пользователь с tg_id {tg_id} не найден")
                    return False
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                await session.rollback()
                return False

    async def create_row(self, tg_id: int) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                personal_data = PersonalData(tg_id=tg_id)
                session.add(personal_data)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при создании строки в PersonalData: %s", e)
                await session.rollback()
                return False

    async def update_all_passport_data(self, tg_id: int, data: list) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                personal_data = PersonalData(tg_id=tg_id)

                # Внесение значений из массива ответов
                personal_data.first_name = data[0]
                personal_data.surname = data[1]
                personal_data.middle_name = data[2]

                personal_data.passport_series = int(data[3])
                personal_data.passport_number = int(data[4])
                personal_data.who_issued_it = data[5]
                personal_data.date_of_issue = datetime.datetime.strptime(data[6], "%Y-%m-%d")
                personal_data.unit_code = data[7]
                personal_data.date_of_birth = datetime.datetime.strptime(data[8], "%Y-%m-%d")
                personal_data.place_of_birth = data[9]
                personal_data.registration_address = data[10]
                personal_data.all_passport_data = 1

                # Добавление пользователя в сессию и сохранение в базу данных
                await session.merge(personal_data)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при создании строки в PersonalData: %s", e)
                await session.rollback()
                return False
