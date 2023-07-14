import datetime

from sqlalchemy import select, and_, update, or_
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
                result = await session.execute(select(Track).where(Track.user_id == tg_id).limit(1))
                track = result.scalar_one_or_none()
                return track is not None
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def has_reject_by_tg_id(self, tg_id: int) -> list[Track] | bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                result = await session.execute(
                    select(Track.status).where(Track.user_id == tg_id, Track.status == "reject"))
                tracks = result.all()
                return tracks
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def check_chat_exists(self, tg_id: int) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                result = await session.execute(
                    select(Track).where(Track.user_id == tg_id, Track.status == "approve").limit(1))
                track = result.scalar_one_or_none()
                return track is not None
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def add_track_to_tracks(self, user_id: int, track_title: str, file_id_audio: str) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                new_track = Track(user_id=user_id, track_title=track_title, file_id_audio=file_id_audio,
                                  datetime=datetime.datetime.now())
                session.add(new_track)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при добавлении нового трека: {e}")
                await session.rollback()
                return False

    async def set_task_msg_id_to_tracks(self, track_id: int, task_msg_id: int) -> bool:
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
                self.logger.error(f"Ошибка при добавлении нового трека: {e}")
                await session.rollback()
                return False

    async def get_id_by_file_id_audio(self, file_id_audio: int) -> int | bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                result = await session.execute(select(Track.id).where(Track.file_id_audio == file_id_audio))
                track_id = result.scalar_one_or_none()
                return track_id
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_task_info_by_id(self, track_id: int):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                result = await session.execute(select(Track.user_id, Track.track_title).where(Track.id == track_id))
                track_info = result.first()
                return track_info
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_custom_answer_info_by_id(self, track_id: int):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                result = await session.execute(
                    select(Track.user_id, Track.track_title).where(Track.id == track_id))
                track_info = result.first()
                return track_info
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_rejected_by_tg_id(self, tg_id: int):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                result = await session.execute(
                    select(Track.track_title, Track.id).where(Track.user_id == tg_id, Track.status == "reject"))
                tracks = result.all()
                return tracks
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_approved_by_tg_id(self, tg_id: int):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                result = await session.execute(
                    select(Track.track_title, Track.id)
                    .where(Track.user_id == tg_id, or_(Track.status == "approve", Track.status == "approve_promo")))
                tracks = result.all()
                return tracks
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def check_count_process_by_tg_id(self, tg_id: int):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                result = await session.execute(
                    select(Track.status).where(Track.user_id == tg_id, Track.status == "process"))
                process_tracks = result.all()
                return len(process_tracks) < 3
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_title_by_track_id(self, track_id: int):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                result = await session.execute(select(Track.track_title).where(Track.id == track_id))
                title = result.scalar_one_or_none()
                return title
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_task_msg_id_by_track_id(self, track_id: int):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                result = await session.execute(select(Track.task_msg_id).where(Track.id == track_id))
                msg_id = result.scalar_one_or_none()
                return msg_id
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_title_and_file_id_by_id(self, track_id: int):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                result = await session.execute(
                    select(Track.track_title, Track.file_id_audio).where(Track.id == track_id))
                row = result.first()
                return row
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def update_track_file_id_audio(self, track_id: int, file_id_audio: int) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                await session.execute(
                    update(Track).where(Track.id == track_id).values(file_id_audio=file_id_audio))
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def set_new_status_track(self, track_id: int, status: str, admin_id=None) -> bool:
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                await session.execute(update(Track).where(Track.id == track_id).values(status=status,
                                                                                       id_who_approve=admin_id))
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние: {e}")
                return False
