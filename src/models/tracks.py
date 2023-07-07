import datetime

from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError

from src.database.process import DatabaseManager
from src.models.tables import Track


class TrackHandler:

    def __init__(self, engine, logger):
        self.engine = engine
        self.logger = logger

    async def has_tracks_by_tg_id(self, tg_id: int) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(Track).where(and_(Track.user_id == int(tg_id))).limit(1)
                result = await session.execute(query)
                chat = result.scalar_one_or_none()
                return chat is not None
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return False

    async def has_reject_by_tg_id(self, tg_id: int, limit: int):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(Track).where(and_(Track.user_id == int(tg_id), Track.reject == True)).limit(limit)
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
        Проверяет наличие строки в таблице Track, где user_id равно tg_id и approve равно True.

        :param tg_id: ID пользователя в Telegram.
        :return: True, если такая строка существует. False в противном случае или если произошла ошибка при выполнении запроса.
        """
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(Track).where(and_(Track.user_id == tg_id, Track.approve is True)).limit(1)
                result = await session.execute(query)
                chat = result.scalar_one_or_none()
                return chat is not None
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return False

    async def add_track_to_tracks(self, user_id: int,
                                  track_title: str,
                                  task_msg_id: int,
                                  file_id_audio: str) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                new_track = Track(user_id=user_id,
                                  track_title=track_title,
                                  task_msg_id=task_msg_id,
                                  file_id_audio=file_id_audio,
                                  datetime=datetime.datetime.now())
                session.add(new_track)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при добавлении нового чата: %s", e)
                await session.rollback()
                return False
