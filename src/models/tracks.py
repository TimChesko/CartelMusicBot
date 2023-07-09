import datetime

from sqlalchemy import select, and_, update
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

    # async def has_reject_by_tg_id(self, tg_id: int, limit: int):
    #     async with DatabaseManager.create_session(self.engine) as session:
    #         try:
    #             query = select(Track).where(and_(Track.user_id == int(tg_id), Track.reject == True)).limit(limit)
    #             result = await session.execute(query)
    #             chat = result.all()
    #             if not chat:
    #                 chat = None
    #             return chat
    #         except SQLAlchemyError as e:
    #             self.logger.error("Ошибка при выполнении запроса: %s", e)
    #             return False

    async def has_reject_by_tg_id(self, tg_id: int):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(Track.reject).where(and_(Track.user_id == int(tg_id)))
                result = await session.execute(query)
                chat = result.all()
                # if chat is None:
                #     return False
                # else:
                #     return True
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
                                  file_id_audio: str) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                new_track = Track(user_id=user_id,
                                  track_title=track_title,
                                  file_id_audio=file_id_audio,
                                  datetime=datetime.datetime.now())
                session.add(new_track)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при добавлении нового чата: %s", e)
                await session.rollback()
                return False

    async def set_task_msg_id_to_tracks(self, track_id, task_msg_id: int) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                track = await session.get(Track, track_id)
                if track:
                    track.task_msg_id = task_msg_id
                    await session.commit()
                    return True
                else:
                    self.logger.error(f"Трек с id {track_id} не найден, set_task_msg_id")
                    return False
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при добавлении нового чата: %s", e)
                await session.rollback()
                return False

    async def get_id_by_file_id_audio(self, file_id_audio):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(Track.id).where(and_(Track.file_id_audio == file_id_audio))
                result = await session.execute(query)
                track_id = result.scalar_one_or_none()
                return track_id
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return False

    async def get_task_info_by_id(self, track_id):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(Track.user_id, Track.track_title).where(and_(Track.id == track_id))
                result = await session.execute(query)
                row = result.first()
                return row
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return False

    # SET STATES FOR TRACKS (process, reject, approve, public & etc)

    async def set_track_to_process(self, track_id):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                await session.execute(
                    update(Track).where(Track.id == track_id).values(process=True,
                                                                     reject=False,
                                                                     approve=False,
                                                                     approve_promo=False,
                                                                     aggregating=False,
                                                                     aggregated=False)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при установке трека в состояние 'в процессе': %s", e)
                return False

    async def set_track_to_reject(self, track_id, listener):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                await session.execute(
                    update(Track).where(Track.id == track_id).values(process=False,
                                                                     reject=True,
                                                                     approve=False,
                                                                     approve_promo=False,
                                                                     aggregating=False,
                                                                     aggregated=False,
                                                                     id_who_approve=listener)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при установке трека в состояние 'в процессе': %s", e)
                return False

    async def set_track_to_approve(self, track_id, listener):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                await session.execute(
                    update(Track).where(Track.id == track_id).values(process=False,
                                                                     reject=False,
                                                                     approve=True,
                                                                     approve_promo=False,
                                                                     aggregating=False,
                                                                     aggregated=False,
                                                                     id_who_approve=listener)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при установке трека в состояние 'в процессе': %s", e)
                return False

    async def set_track_to_approve_promo(self, track_id, listener):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                await session.execute(
                    update(Track).where(Track.id == track_id).values(process=False,
                                                                     reject=False,
                                                                     approve=False,
                                                                     approve_promo=True,
                                                                     aggregating=False,
                                                                     aggregated=False,
                                                                     id_who_approve=listener)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при установке трека в состояние 'в процессе': %s", e)
                return False

    async def set_track_to_aggregating(self, track_id):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                await session.execute(
                    update(Track).where(Track.id == track_id).values(process=False,
                                                                     reject=False,
                                                                     approve=False,
                                                                     approve_promo=False,
                                                                     aggregating=True,
                                                                     aggregated=False)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при установке трека в состояние 'в процессе': %s", e)
                return False

    async def set_track_to_aggregated(self, track_id):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                await session.execute(
                    update(Track).where(Track.id == track_id).values(process=False,
                                                                     reject=False,
                                                                     approve=False,
                                                                     approve_promo=False,
                                                                     aggregating=False,
                                                                     aggregated=True)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при установке трека в состояние 'в процессе': %s", e)
                return False
