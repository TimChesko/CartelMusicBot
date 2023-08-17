import datetime

from sqlalchemy import select, update, or_, asc, and_, delete
from sqlalchemy.exc import SQLAlchemyError

from src.data.config import Config
from src.models.tables import Track, User, TrackInfo
from src.utils.enums import Status


class TrackHandler:

    def __init__(self, session_maker, logger):
        self.session_maker = session_maker
        self.logger = logger

    async def get_tracks_by_status(self, tg_id: int, status: str):
        async with self.session_maker() as session:
            try:
                query = select(Track).where(and_(Track.user_id == tg_id, Track.status == status))
                result = await session.execute(query)
                return result.scalars().all()
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса get_tracks_by_status: {e}")
                return False

    async def get_tracks_and_info_by_status(self, user_id: int, status: str):
        async with self.session_maker() as session:
            try:
                query = select(Track, TrackInfo).join(TrackInfo, Track.id == TrackInfo.track_id).where(
                    (Track.user_id == user_id) &
                    (or_(Track.status == status, TrackInfo.status == status))
                )
                result = await session.execute(query)
                return result.all()
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return []

    async def get_track_by_id(self, track_id: int):
        async with self.session_maker() as session:
            try:
                query = select(Track).where(Track.id == track_id)
                result = await session.execute(query)
                return result.scalar()
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса get_tracks_by_status: {e}")
                return False

    async def delete_track_by_id(self, track_id: int):
        async with self.session_maker() as session:
            try:
                # Получаем экземпляр трека для удаления
                query = select(Track).where(Track.id == track_id)
                result = await session.execute(query)
                track_instance = result.scalar()
                if track_instance:
                    await session.execute(delete(TrackInfo).where(TrackInfo.track_id == track_id))
                    await session.execute(delete(Track).where(Track.id == track_id))
                    await session.commit()
                    return True
                else:
                    return False
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса delete_track_by_id: {e}")
                await session.rollback()
                return False

    async def has_tracks_by_tg_id(self, tg_id: int) -> bool:
        async with self.session_maker() as session:
            try:
                result = await session.execute(select(Track).where(Track.user_id == tg_id).limit(1))
                track = result.scalar_one_or_none()
                return track is not None
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса has_tracks_by_tg_id: {e}")
                return False

    async def has_reject_by_tg_id(self, tg_id: int) -> list[Track] | bool:
        async with self.session_maker() as session:
            try:
                query = select(Track.status).where(and_(
                    Track.user_id == tg_id, Track.status == Status.REJECT))
                result = await session.execute(query)
                return result.all()
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def check_chat_exists(self, tg_id: int) -> bool:
        async with self.session_maker() as session:
            try:
                query = select(Track).where(Track.user_id == tg_id).limit(1)
                result = await session.execute(query)
                return result.scalar_one_or_none() is not None
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса check_chat_exists: {e}")
                return False

    async def add_new_track(self, user_id: int, track_title: str, file_id_audio: str) -> bool:
        async with self.session_maker() as session:
            try:
                new_track = Track(user_id=user_id,
                                  track_title=track_title,
                                  file_id_audio=file_id_audio)
                session.add(new_track)
                await session.flush()  # Это обновит new_track.id после добавления в базу данных
                new_info = TrackInfo(track_id=new_track.id)
                session.add(new_info)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при добавлении нового трека: {e}")
                await session.rollback()
                return False

    async def get_task_info_by_id(self, track_id: int):
        async with self.session_maker() as session:
            try:
                result = await session.execute(select(Track.user_id, Track.track_title).where(Track.id == track_id))
                track_info = result.first()
                return track_info
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_custom_answer_info_by_id(self, track_id: int):
        async with self.session_maker() as session:
            try:
                query = select(Track.user_id, Track.track_title).where(Track.id == track_id)
                result = await session.execute(query)
                return result.first()
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_rejected_by_tg_id(self, tg_id: int):
        async with self.session_maker() as session:
            try:
                query = select(Track).where(and_(Track.user_id == tg_id, Track.status == Status.REJECT))
                result = await session.execute(query)
                return result.all()
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_approved_by_tg_id(self, tg_id: int):
        async with self.session_maker() as session:
            try:
                query = select(Track.track_title, Track.id).where(and_(
                    Track.user_id == tg_id, Track.status == Status.APPROVE))
                result = await session.execute(query)
                return result.all()
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def check_count_process_by_tg_id(self, tg_id: int):
        async with self.session_maker() as session:
            try:
                query = select(Track.status).where(and_(
                    Track.user_id == tg_id, Track.status == Status.PROCESS))
                result = await session.execute(query)
                process_tracks = result.all()
                return len(process_tracks) < 3
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_process_tracks(self):
        async with self.session_maker() as session:
            try:
                query = select(Track.id).where(
                    and_(Track.status == Status.PROCESS, Track.checker_id.is_(None))).order_by(
                    asc(Track.date_last_edit))
                result = await session.execute(query)
                return result.all()
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def update_edited_track(self, track_id: int, file_id_audio: int) -> bool:
        async with self.session_maker() as session:
            try:
                query = update(Track).where(Track.id == track_id).values(
                    file_id_audio=file_id_audio,
                    date_last_edit=datetime.datetime.now(),
                    status=Status.PROCESS)
                await session.execute(query)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def get_listening_info(self, track_id: int):
        async with self.session_maker() as session:
            try:
                query = select(Track.checker_id, Track.file_id_audio, Track.track_title, User).join(User).where(
                    Track.id == track_id)
                result = await session.execute(query)
                tracks = result.first()
                return tracks
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def update_checker(self, track_id: int, employee_id=None) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Track).where(Track.id == track_id).values(
                        checker=employee_id,
                        status=Status.REJECT)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def set_task_state(self, track_id, employee_id=None) -> bool:
        async with self.session_maker() as session:
            try:
                query = update(Track).where(Track.id == track_id).values(checker_id=employee_id)
                await session.execute(query)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def update_release_id(self, track_ids: list, release_id) -> bool:
        async with self.session_maker() as session:
            try:
                query = update(Track).where(Track.id.in_(track_ids)).values(release_id=release_id)
                await session.execute(query)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def update_approve(self, track_id: int, employee_id: int, config: Config) -> bool:
        async with self.session_maker() as session:
            try:
                if employee_id in config.constant.developers:
                    employee_id = None

                query_update = update(Track).where(Track.id == track_id).values(
                    id_who_approve=employee_id,
                    track_state=Status.APPROVE)
                await session.execute(query_update)
                await session.commit()

                query_getter = select(Track.user_id).where(Track.id == track_id)
                result = await session.execute(query_getter)
                return result.scalar_one_or_none()
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def get_for_release_multiselect(self, tg_id: int):
        async with self.session_maker() as session:
            try:
                query = select(Track.track_title, Track.id).join(TrackInfo).where(and_(
                    Track.user_id == tg_id,
                    Track.release_id.is_(None),
                    TrackInfo.status == Status.APPROVE,
                    Track.status == Status.APPROVE))
                result = await session.execute(query)
                return result.all()
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False
