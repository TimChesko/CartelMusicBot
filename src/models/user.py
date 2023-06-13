from aiogram.types import Message
from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError

from src.database.process import DatabaseManager
from src.models.tables import User


class UserHandler:

    def __init__(self, engine, logger):
        self.engine = engine
        self.logger = logger

    async def get_all_by_tg_id(self, tg_id: int):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(User).where(and_(User.tg_id == tg_id))
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                return user
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса:", e)
                return False

    async def get_ban_by_tg_id(self, tg_id: int):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(User.ban).where(and_(User.tg_id == tg_id))
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                return user
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса:", e)
                return False

    async def add_new_user(self, msg: Message) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                new_user = User(tg_id=msg.from_user.id, tg_username=msg.from_user.username,
                                tg_first_name=msg.from_user.first_name, tg_last_name=msg.from_user.last_name)
                session.add(new_user)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при добавлении нового пользователя:", e)
                session.rollback()
                return False
