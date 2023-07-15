import datetime

from sqlalchemy import select, and_, update
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
                    await self.create_row(tg_id)
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

    async def update_all_personal_data(self, tg_id: int, personal_data: str, save_input: dict) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                existing_data = await session.execute(select(PersonalData).where(PersonalData.tg_id == tg_id))
                existing_data = (existing_data.first())[0] if existing_data else None

                if existing_data:
                    for key, value in save_input.items():
                        setattr(existing_data, key, value)
                    if personal_data == "passport":
                        existing_data.all_passport_data = 1
                    elif personal_data == "bank":
                        existing_data.all_bank_data = 1
                else:
                    if personal_data == "passport":
                        save_input["all_passport_data"] = 1
                    elif personal_data == "bank":
                        save_input["all_bank_data"] = 1
                    personal_data = PersonalData(tg_id=tg_id, **save_input)
                    session.add(personal_data)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при обновлении персональных данных: %s", e)
                await session.rollback()
                return False

    async def find_none_columns_passport(self, tg_id: int) -> list:
        none_columns = []
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(PersonalData).where(PersonalData.tg_id == tg_id)
                result = await session.execute(query)
                personal_data = result.scalar_one_or_none()
                if personal_data:
                    columns_to_check = [
                        PersonalData.first_name,
                        PersonalData.surname,
                        PersonalData.middle_name,
                        PersonalData.passport_series,
                        PersonalData.passport_number,
                        PersonalData.who_issued_it,
                        PersonalData.date_of_issue,
                        PersonalData.unit_code,
                        PersonalData.date_of_birth,
                        PersonalData.place_of_birth,
                        PersonalData.registration_address,
                    ]
                    for column in columns_to_check:
                        column_value = getattr(personal_data, column.name)
                        if column_value is None:
                            none_columns.append(column.name)
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при поиске всех None в passport: %s", e)
        return none_columns

    async def find_none_columns_bank(self, tg_id: int) -> list:
        none_columns = []
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(PersonalData).where(PersonalData.tg_id == tg_id)
                result = await session.execute(query)
                personal_data = result.scalar_one_or_none()
                if personal_data:
                    columns_to_check = [
                        PersonalData.recipient,
                        PersonalData.account_code,
                        PersonalData.bik_code,
                        PersonalData.bank_recipient,
                        PersonalData.correct_code,
                        PersonalData.inn_code,
                        PersonalData.kpp_code,
                        PersonalData.swift_code,
                    ]
                    for column in columns_to_check:
                        column_value = getattr(personal_data, column.name)
                        if column_value is None:
                            none_columns.append(column.name)
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при поиске всех None в bank: %s", e)
        return none_columns

    async def update_personal_data(self, user_id: int, found_key: str, data, location: str, count_edit: int) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                if location == "password":
                    update_data = {found_key: data, "all_passport_data": 2 if count_edit > 1 else 1}
                elif location == "bank":
                    update_data = {found_key: data, "all_passport_data": 2 if count_edit > 1 else 1}
                else:
                    return False
                query = update(PersonalData).where(PersonalData.tg_id == user_id).values(**update_data)
                await session.execute(query)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при обновлении значения в таблице PersonalData: %s", e)
                await session.rollback()
                return False
