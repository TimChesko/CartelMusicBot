import datetime

from sqlalchemy import select, update, or_, asc, and_, delete
from sqlalchemy.exc import SQLAlchemyError

from src.models.tables import Track, User, TrackInfo, PersonalData


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
                    and_(Track.status == 'process', Track.checker is None)).order_by(asc(Track.sort_datetime))
                result = await session.execute(query)
                tracks = result.all()
                return tracks
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def update_edited_track(self, track_id: int, file_id_audio: int) -> bool:
        async with self.session_maker() as session:
            try:
                query = update(Track).where(Track.id == track_id).values(file_id_audio=file_id_audio,
                                                                         sort_datetime=datetime.datetime.now(),
                                                                         status='process')
                await session.execute(query)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def get_listening_info(self, track_id: int):
        async with self.session_maker() as session:
            try:
                query = select(Track).join(User).where(Track.id == track_id)
                result = await session.execute(query)
                tracks = result.scalars().all()
                return tracks
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
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

    async def add_track_info(self, data: dict):
        async with self.session_maker() as session:
            try:
                new_track_info = TrackInfo(**data)
                session.add(new_track_info)
                await session.commit()
                return new_track_info.id
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при добавлении нового трека: {e}")
                await session.rollback()
                return False

    async def update_track_info_feat(self, track_id: int, user_id: int) -> list[bool, str]:
        async with self.session_maker() as session:
            try:
                # Заблокировать строку и получить данные
                result = await session.execute(
                    select(TrackInfo, Track, PersonalData).join_from(
                        TrackInfo, Track, TrackInfo.track_id == Track.id
                    ).join(
                        PersonalData, Track.user_id == PersonalData.tg_id
                    ).where(
                        TrackInfo.id == track_id,
                        TrackInfo.feat_tg_id.is_(None),
                        Track.user_id != user_id
                    ).with_for_update()
                )

                track_info, track, personal_data = result.scalar_one_or_none()

                if not track_info or not track or not personal_data:
                    return [False, "Ошибка, нет возможности прикрепить данного пользователя."]

                # Указываем что feat_tg_id=str(user_id)
                track_info.feat_tg_id = str(user_id)

                # Если оба значения равны 3, то записать в TrackInfo.status="process"
                if personal_data.all_passport_data == 3 and personal_data.all_bank_data == 3:
                    track_info.status = "process"
                    text_status = "трек отправлен на модерацию!"
                else:
                    # В другом случае TrackInfo.status="wait_docs_feat"
                    track_info.status = "wait_docs_feat"
                    text_status = "пройдите верификацию, чтобы отправить трек на модерацию."
                await session.commit()

                return [True, f"Данные обновлены, {text_status}"]
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при обновлении информации о треке: {e}")
                await session.rollback()
                return [False, "Ошибка на стороне сервера, обратитесь в службу поддержки.\n/support"]


