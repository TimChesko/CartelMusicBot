import logging

from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError

from src.models.tables import PersonalData, Social, PersonalDataTemplate


class PersonalDataHandler:

    def __init__(self, session_maker, logger):
        self.session_maker = session_maker
        self.logger = logger

    async def get_all_data_status(self, tg_id: int) -> tuple[str, str] | tuple[None, None]:
        async with self.session_maker() as session:
            try:
                logging.debug(tg_id)
                logging.debug(type(tg_id))
                query = select(PersonalData).where(PersonalData.tg_id == tg_id)
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                if user:
                    return user.all_passport_data, user.all_bank_data
                else:
                    self.logger.error(f"Пользователь с tg_id {tg_id} не найден. Создание новой записи.")
                    new_user = PersonalData(tg_id=tg_id)
                    session.add(new_user)
                    await session.commit()
                    return None, None
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса get_all_data_status: %s", e)
                await session.rollback()
                return None, None

    async def get_personal_data_confirm(self, tg_id: int) -> bool:
        async with self.session_maker() as session:
            try:
                query = select(PersonalData).where(PersonalData.tg_id == tg_id)
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
        async with self.session_maker() as session:
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
        async with self.session_maker() as session:
            try:
                personal_data = PersonalData(tg_id=tg_id)
                session.add(personal_data)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при создании строки в PersonalData: %s", e)
                await session.rollback()
                return False

    async def update_all_personal_data(self, tg_id: int, header_data: str, save_input: dict) -> bool:
        async with self.session_maker() as session:
            try:
                existing_data = await session.execute(select(PersonalData).where(PersonalData.tg_id == tg_id))
                existing_data = (existing_data.first())[0] if existing_data else None

                if existing_data:
                    for key, value in save_input.items():
                        setattr(existing_data, key, value)
                    if header_data == "passport":
                        existing_data.all_passport_data = "process"
                    elif header_data == "bank":
                        existing_data.all_bank_data = "process"
                else:
                    if header_data == "passport":
                        save_input["all_passport_data"] = "process"
                    elif header_data == "bank":
                        save_input["all_bank_data"] = "process"
                    header_data = PersonalData(tg_id=tg_id, **save_input)
                    session.add(header_data)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при обновлении персональных данных: %s", e)
                await session.rollback()
                return False

    async def get_social_data(self, tg_id: int):
        async with self.session_maker() as session:
            try:
                query = select(Social).where(Social.personal_data_tg_id == tg_id)
                result = await session.execute(query)
                social_data = result.scalars().all()
                social_data_with_id = [(row.id, row.title, row.link) for row in social_data]
                return social_data_with_id
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при получении данных из таблицы Social: %s", e)
                return []

    async def get_social_by_id(self, social_id: int):
        async with self.session_maker() as session:
            try:
                query = select(Social).where(Social.id == social_id)
                result = await session.execute(query)
                social_data = result.scalar_one_or_none()
                if social_data:
                    return [social_data.id, social_data.title, social_data.link]
                else:
                    return None
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при получении данных из таблицы Social: %s", e)
                return None

    async def add_social_data(self, tg_id: int, title: str, link: str) -> bool:
        async with self.session_maker() as session:
            try:
                social_data = Social(personal_data_tg_id=tg_id, title=title, link=link)
                session.add(social_data)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при добавлении данных в таблицу Social: %s", e)
                await session.rollback()
                return False

    async def delete_social_data(self, social_id: int) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    delete(Social).where(Social.id == social_id)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при удалении данных из таблицы Social: %s", e)
                await session.rollback()
                return False

    async def update_personal_data(self, tg_id: int, header_data: str, data: dict) -> bool:
        async with self.session_maker() as session:
            try:
                personal_data_query = select(PersonalData).where(PersonalData.tg_id == tg_id)
                personal_data_result = await session.execute(personal_data_query)
                personal_data = personal_data_result.scalar_one_or_none()

                template_query = select(PersonalDataTemplate.name_data).where(
                    PersonalDataTemplate.header_data == header_data)
                template_result = await session.execute(template_query)
                list_name_data = template_result.scalars().all()

                count_none = sum(1 for key in list_name_data if getattr(personal_data, key) is None)
                self.logger.info(count_none)
                all_data_field = f"all_{header_data}_data"
                self.logger.info(all_data_field)
                if hasattr(PersonalData, all_data_field):
                    setattr(personal_data, all_data_field, 2 if count_none > 1 else 1)

                for key, value in data.items():
                    if hasattr(PersonalData, key):
                        setattr(personal_data, key, value)

                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при обновлении данных в: %s", e)
                await session.rollback()
                return False

    async def get_personal_data_by_header(self, tg_id: int, header_data: str):
        async with self.session_maker() as session:
            try:
                # Fetch the personal data for the given tg_id
                personal_data_query = select(PersonalData).where(PersonalData.tg_id == tg_id)
                personal_data_result = await session.execute(personal_data_query)
                personal_data = personal_data_result.scalar_one_or_none()

                # Fetch the name_data, text, example, and input_type values for the given header_data
                template_query = select(
                    PersonalDataTemplate.name_data,
                    PersonalDataTemplate.title,
                    PersonalDataTemplate.text,
                    PersonalDataTemplate.example,
                    PersonalDataTemplate.input_type
                ).where(PersonalDataTemplate.header_data == header_data).order_by(PersonalDataTemplate.id)
                template_result = await session.execute(template_query)
                template_data = template_result.all()

                # Find the columns with None values
                none_columns = [(name_data, title, text, example, input_type)
                                for name_data, title, text, example, input_type in template_data
                                if getattr(personal_data, name_data) is None]

                return none_columns
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при получении данных из таблицы PersonalData: %s", e)
                return []

    async def get_docs_passport(self) -> list | None:
        async with self.session_maker() as session:
            try:
                query = select(PersonalData).where(PersonalData.all_passport_data == 1).\
                    order_by(PersonalData.add_datetime.asc())
                result = await session.execute(query)
                return result.scalars().all()
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return None

    async def get_data_by_tg(self, tg_id: int):
        async with self.session_maker() as session:
            try:
                query = select(PersonalData).where(PersonalData.tg_id == tg_id)
                result = await session.execute(query)
                return result.scalar()
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return None


