import datetime

from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError

from src.database.process import DatabaseManager
from src.models.tables import Chats


class ChatsHandler:

    def __init__(self, engine, logger):
        self.engine = engine
        self.logger = logger

    async def has_chats_by_tg_id(self, tg_id: int) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(Chats).where(and_(Chats.user_id == int(tg_id))).limit(1)
                result = await session.execute(query)
                chat = result.scalar_one_or_none()
                return chat is not None
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return False

    async def has_reject_by_tg_id(self, tg_id: int, limit: int):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(Chats).where(and_(Chats.user_id == int(tg_id), Chats.reject == True)).limit(limit)
                result = await session.execute(query)
                chat = result.all()
                if not chat:
                    chat = None
                return chat
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return False

    async def check_chat_exists(self, tg_id: int) -> bool:
        """
        Проверяет наличие строки в таблице Chats, где user_id равно tg_id и approve равно True.

        :param tg_id: ID пользователя в Telegram.
        :return: True, если такая строка существует. False в противном случае или если произошла ошибка при выполнении запроса.
        """
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(Chats).where(and_(Chats.user_id == tg_id, Chats.approve is True)).limit(1)
                result = await session.execute(query)
                chat = result.scalar_one_or_none()
                return chat is not None
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return False

    async def add_track_to_chat(self, chat_id: int, user_id: int,
                                track_title: str,
                                message_id_audio: int, message_id_audio_text: int,
                                file_id_audio: str, file_id_text: str) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                new_chat = Chats(chat_id=chat_id,
                                 user_id=user_id,
                                 track_title=track_title,
                                 message_id_audio=message_id_audio,
                                 message_id_audio_text=message_id_audio_text,
                                 file_id_audio=file_id_audio,
                                 file_id_text=file_id_text,
                                 datetime=datetime.datetime.now())
                session.add(new_chat)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при добавлении нового чата: %s", e)
                await session.rollback()
                return False
