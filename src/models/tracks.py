from datetime import datetime

from sqlalchemy import select, update, or_, asc, and_, delete
from sqlalchemy.exc import SQLAlchemyError

from src.models.logs.emp import LogEmp
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

    async def get_tracks_and_info_by_status(self, user_id: int, status: Status):
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
                self.logger.error(f"Ошибка при выполнении запроса get_track_by_id: {e}")
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
                result = await session.execute(
                    select(Track).where(and_(Track.user_id == tg_id, Track.status == Status.REJECT)))
                tracks = result.scalars().all()
                return tracks
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def check_tracks_exists(self, tg_id: int) -> bool:
        async with self.session_maker() as session:
            try:
                query = select(Track).where(Track.user_id == tg_id).limit(1)
                result = await session.execute(query)
                track = result.scalar_one_or_none()
                return track is not None
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса check_chat_exists: {e}")
                return False

    async def check_feat_exists(self, tg_id: int) -> bool:
        async with self.session_maker() as session:
            try:
                query = select(TrackInfo).where(TrackInfo.feat_tg_id == tg_id).limit(1)
                result = await session.execute(query)
                track_feat = result.scalar_one_or_none()
                return track_feat is not None
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса check_chat_exists: {e}")
                return False

    async def add_new_track(self, user_id: int, track_title: str, file_id_audio: str) -> bool:
        async with self.session_maker() as session:
            try:
                new_track = Track(user_id=user_id, track_title=track_title, file_id_audio=file_id_audio)
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

    async def check_count_process_by_tg_id(self, tg_id: int):
        async with self.session_maker() as session:
            try:
                result = await session.execute(
                    select(Track.status).where(
                        and_(Track.user_id == tg_id, Track.status == Status.PROCESS)))
                process_tracks = result.all()
                return len(process_tracks) < 3
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_process_tracks(self):
        async with self.session_maker() as session:
            try:
                query = select(Track.id).where(
                    and_(Track.status == Status.PROCESS, Track.checker_id == None)).order_by(
                    asc(Track.date_last_edit))
                result = await session.execute(query)
                tracks = result.all()
                return tracks
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def update_edited_track(self, track_id: int, file_id_audio: int) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Track).where(Track.id == track_id).values(file_id_audio=file_id_audio,
                                                                     date_last_edit=datetime.utcnow(),
                                                                     checker_id=None,
                                                                     status=Status.PROCESS)
                )
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

    async def update_checker(self, track_id: int, employee_id: int, comment: str) -> bool:
        async with self.session_maker() as session:
            try:
                track = await session.get(Track, track_id)
                if not track:
                    self.logger.error(f"Трек с ID {track_id} не найден")
                    return False
                track.checker, track.status = None, Status.REJECT
                LogEmp(employee_id, track.id).track_reject(comment)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def set_task_state(self, track_id, employee_id=None) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Track).where(Track.id == track_id).values(checker_id=employee_id)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def update_release_id(self, track_ids: list, release_id) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Track).where(Track.id.in_(track_ids)).values(release_id=release_id)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def update_approve(self, track_id: int, employee_id: int):
        async with self.session_maker() as session:
            try:
                track = await session.get(Track, track_id)
                if not track:
                    self.logger.error(f"Трек с ID {track_id} не найден")
                    return False
                track.status = Status.APPROVE
                session.add(LogEmp(employee_id, track.id).track_approve())
                await session.commit()
                return track.user_id, track.track_title
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_for_release_multiselect(self, tg_id: int):
        async with self.session_maker() as session:
            try:
                result = await session.execute(
                    select(Track.track_title, Track.id).join(TrackInfo)
                    .where(and_(Track.user_id == tg_id, Track.release_id == None,
                                TrackInfo.status == Status.APPROVE)))
                tracks = result.all()
                return tracks
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_tracks_by_release(self, release_id: int):
        async with self.session_maker() as session:
            try:
                query = select(Track.id, Track.track_title).where(Track.release_id == release_id)
                result = await session.execute(query)
                tracks = result.all()
                return tracks
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False
