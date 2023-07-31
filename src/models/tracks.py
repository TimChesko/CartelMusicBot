import datetime

from sqlalchemy import select, update, or_, asc, and_, delete
from sqlalchemy.exc import SQLAlchemyError

from src.models.tables import Track, User, TrackInfo


class TrackHandler:

    def __init__(self, session_maker, logger):
        self.session_maker = session_maker
        self.logger = logger

    async def has_tracks_by_tg_id(self, tg_id: int) -> bool:
        async with self.session_maker() as session:
            try:
                result = await session.execute(select(Track).where(Track.user_id == tg_id).limit(1))
                track = result.scalar_one_or_none()
                return track is not None
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def has_reject_by_tg_id(self, tg_id: int) -> list[Track] | bool:
        async with self.session_maker() as session:
            try:
                result = await session.execute(
                    select(Track.status).where(Track.user_id == tg_id, Track.status == "reject"))
                tracks = result.all()
                return tracks
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def check_chat_exists(self, tg_id: int) -> bool:
        async with self.session_maker() as session:
            try:
                result = await session.execute(
                    select(Track).where(Track.user_id == tg_id, Track.status == "approve").limit(1))
                track = result.scalar_one_or_none()
                return track is not None
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def add_new_track(self, user_id: int, track_title: str, file_id_audio: str) -> bool:
        async with self.session_maker() as session:
            try:
                new_track = Track(user_id=user_id, track_title=track_title, file_id_audio=file_id_audio,
                                  add_datetime=datetime.datetime.now(), sort_datetime=datetime.datetime.now())
                session.add(new_track)
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
                result = await session.execute(
                    select(Track.user_id, Track.track_title).where(Track.id == track_id))
                track_info = result.first()
                return track_info
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_rejected_by_tg_id(self, tg_id: int):
        async with self.session_maker() as session:
            try:
                result = await session.execute(
                    select(Track.track_title, Track.id).where(Track.user_id == tg_id, Track.status == "reject"))
                tracks = result.all()
                return tracks
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_approved_by_tg_id(self, tg_id: int):
        async with self.session_maker() as session:
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
        async with self.session_maker() as session:
            try:
                result = await session.execute(
                    select(Track.status).where(Track.user_id == tg_id, Track.status == "process"))
                process_tracks = result.all()
                return len(process_tracks) < 3
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_title_by_track_id(self, track_id: int):
        async with self.session_maker() as session:
            try:
                result = await session.execute(select(Track.track_title).where(Track.id == track_id))
                title = result.scalar_one_or_none()
                return title
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_task_msg_id_by_track_id(self, track_id: int):
        async with self.session_maker() as session:
            try:
                result = await session.execute(select(Track.task_msg_id).where(Track.id == track_id))
                msg_id = result.scalar_one_or_none()
                return msg_id
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_user_id_by_track_id(self, track_id: int):
        async with self.session_maker() as session:
            try:
                result = await session.execute(select(Track.user_id).where(Track.id == track_id))
                user_id = result.scalar_one_or_none()
                return user_id
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_title(self, track_id: int):
        async with self.session_maker() as session:
            try:
                result = await session.execute(
                    select(Track.track_title).where(Track.id == track_id))
                row = result.first()
                return row
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_process_tracks(self):
        async with self.session_maker() as session:
            try:
                query = select(Track.id, Track.track_title).where(
                    and_(Track.status == 'process', Track.checker == None)).order_by(asc(Track.sort_datetime))
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
                                                                     sort_datetime=datetime.datetime.now(),
                                                                     status='process')
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def get_listening_info(self, track_id: int):
        async with self.session_maker() as session:
            try:
                query = select(Track.checker, Track.file_id_audio, User).join(User).where(Track.id == track_id)
                result = await session.execute(query)
                tracks = result.first()
                return tracks
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def update_checker(self, track_id, employee_id=None) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Track).where(Track.id == track_id).values(checker=employee_id,
                                                                     status='reject')
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def update_approve(self, track_id, employee_id) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Track).where(Track.id == track_id).values(id_who_approve=employee_id,
                                                                     status='approve')
                )
                query = select(Track.user_id).where(Track.id == track_id)
                result = await session.execute(query)
                user_id = result.scalar_one_or_none()
                await session.commit()
                return user_id
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def get_tracks_by_status(self, user_id: int, status: str):
        async with self.session_maker() as session:
            try:
                query = select(Track).where(and_(Track.user_id == user_id, Track.status == status))
                result = await session.execute(query)
                return result.scalars().all()
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при получения треков в статусу: {e}")
                return False

    async def get_track_by_id(self, track_id: int):
        async with self.session_maker() as session:
            try:
                query = select(Track).where(Track.id == track_id)
                result = await session.execute(query)
                return result.scalar()
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def delete_track_by_id(self, track_id: int) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(delete(Track).where(Track.id == track_id))
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при удалении трека: {e}")
                return False

    async def add_track_info(self, data: dict) -> bool:
        async with self.session_maker() as session:
            try:
                new_track_info = TrackInfo(**data)
                session.add(new_track_info)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при добавлении нового трека: {e}")
                await session.rollback()
                return False

    async def update_track_info_feat(self, track_id: int, user_id: int) -> bool:
        async with self.session_maker() as session:
            try:
                # Обновляем только те строки, где feat_tg_id is None
                query = (
                    update(TrackInfo)
                    .where(TrackInfo.id == track_id, TrackInfo.feat_tg_id.is_(None))
                    .values(feat_tg_id=str(user_id))
                )
                result = await session.execute(query)
                await session.commit()

                # Если была обновлена хотя бы одна строка, возвращаем True
                return result.rowcount > 0
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при обновлении информации о треке: {e}")
                await session.rollback()
                return False
