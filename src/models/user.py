from aiogram.types import Message
from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError

from src.database.process import DatabaseManager
from src.models.tables import User


class UserHandler:

    def __init__(self, engine, logger):
        self.engine = engine
        self.logger = logger

    async def get_nicknames_by_tg_id(self, tg_id: int):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(User.nickname, User.tg_username).where(and_(User.tg_id == tg_id))
                result = await session.execute(query)
                row = result.first()
                return row
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return False

    async def get_ban_by_tg_id(self, tg_id: int):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(User.ban).where(and_(User.tg_id == tg_id))
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                return user
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return False

    async def get_privilege_by_tg_id(self, tg_id: int):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(User.privilege).where(and_(User.tg_id == tg_id))
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                return user
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
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
                self.logger.error("Ошибка при добавлении нового пользователя: %s", e)
                await session.rollback()
                return False

    async def set_user_nickname(self, user_id: int, user_nickname: str) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                user = await session.get(User, user_id)
                if user:
                    user.nickname = user_nickname
                    await session.commit()
                    return True
                else:
                    self.logger.error(f"Пользователь с tg_id {user_id} не найден, set_user_nickname")
                    return False
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при изменении никнейма: %s", e)
                await session.rollback()
                return False

    async def get_user_nickname_by_tg_id(self, tg_id: int):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(User.nickname).where(and_(User.tg_id == tg_id))
                result = await session.execute(query)
                nickname = result.scalar_one_or_none()
                return nickname
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при добавлении нового пользователя: %s", e)
                return False

    async def set_privilege(self, user_id: int, new_privilege: str) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                user = await session.get(User, user_id)
                if user:
                    user.privilege = new_privilege
                    await session.commit()
                    return True
                else:
                    self.logger.error(f"Пользователь с tg_id {user_id} не найден, set_privilege")
                    return False
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при добавлении нового пользователя: %s", e)
                await session.rollback()
                return False
