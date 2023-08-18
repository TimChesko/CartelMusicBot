from aiogram.types import Message
from sqlalchemy import update, select
from sqlalchemy.exc import SQLAlchemyError

from src.models.tables import User, PersonalData


class UserHandler:

    def __init__(self, session_maker, logger):
        self.session_maker = session_maker
        self.logger = logger

    async def get_user_by_tg_id(self, tg_id: int):
        async with self.session_maker() as session:
            try:
                query = select(User).where(User.tg_id == tg_id)
                user = await session.execute(query)
                return user.scalar_one_or_none()
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return False

    async def add_new_user(self, msg: Message) -> bool:
        async with self.session_maker() as session:
            try:
                new_user = User(
                    tg_id=msg.from_user.id,
                    tg_username=msg.from_user.username,
                    tg_first_name=msg.from_user.first_name,
                    tg_last_name=msg.from_user.last_name
                )
                session.add(new_user)
                personal_data = PersonalData(tg_id=msg.from_user.id)
                session.add(personal_data)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при добавлении нового пользователя: %s", e)
                await session.rollback()
                return False

    async def update_nickname(self, tg_id: int, nickname: str) -> bool:
        async with self.session_maker() as session:
            try:
                query = update(User).where(User.tg_id == tg_id).values({"nickname": nickname})
                await session.execute(query)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при обновлении nickname в таблице UserHandler: %s", e)
                await session.rollback()
                return False
