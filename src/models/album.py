import datetime

from sqlalchemy import select, update, delete, asc
from sqlalchemy.exc import SQLAlchemyError

from src.models.tables import Album, Track, User, PersonalData


# noinspection PyTypeChecker
class AlbumHandler:

    def __init__(self, session_maker, logger):
        self.session_maker = session_maker
        self.logger = logger

    async def add_new_album(self, user_id: int) -> bool:
        async with self.session_maker() as session:
            try:
                new_track = Album(user_id=user_id, create_datetime=datetime.datetime.now())
                session.add(new_track)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при добавлении нового трека: {e}")
                await session.rollback()
                return False

    async def get_album_by_user_id(self, user_id):
        async with self.session_maker() as session:
            try:
                result = await session.execute(select(Album.id, Album.album_title).where(Album.user_id == user_id))
                track_info = result.all()
                return track_info
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_unsigned_state(self, state):
        async with self.session_maker() as session:
            try:
                result = await session.execute(
                    select(Album).where(Album.unsigned_state == state).order_by(
                        asc(Album.sort_datetime))
                )
                track_info = result.scalars().all()
                return track_info
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_album_scalar(self, album_id) -> Album:
        async with self.session_maker() as session:
            try:
                album = await session.execute(select(Album).where(Album.id == album_id))
                album_info = album.scalar_one_or_none()
                tracks = await session.execute(select(Track.track_title).where(Track.album_id == album_id))
                tracks_info = tracks.scalars().all()
                return album_info, tracks_info if len(tracks_info) > 0 else None
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def delete_album_id_from_tracks(self, album_id) -> Album:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Track).where(Track.album_id == album_id).values(album_id=None)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def delete_release(self, album_id) -> Album:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Track).where(Track.album_id == album_id).values(album_id=None)
                )
                await session.execute(
                    delete(Album).where(Album.id == album_id)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_tracks_and_personal_data(self, tg_id: int, album_id: int):
        async with self.session_maker() as session:
            try:
                user = await session.execute(select(User).where(User.tg_id == tg_id))
                user = user.scalar_one()
                album = await session.execute(select(Album).where(Album.id == album_id))
                album = album.scalar_one()
                tracks = await session.execute(select(Track).where(Track.album_id == album_id))
                tracks = tracks.scalars().all()
                return user, tracks, album
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_release_lvl1_info(self, album_id: int):
        async with self.session_maker() as session:
            try:
                query = select(Album, User).join(User).where(Album.id == album_id)
                result = await session.execute(query)
                tracks = result.first()
                return tracks
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_album_first(self, album_id: int) -> Album:
        async with self.session_maker() as session:
            try:
                query = select(Album).where(Album.id == album_id)
                result = await session.execute(query)
                tracks = result.scalar()
                return tracks
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def set_task_state(self, album_id, employee_id=None) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Album).where(Album.id == album_id).values(checker=employee_id)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def approve(self, album_id, employee_id, state) -> bool:
        async with self.session_maker() as session:
            try:
                if state == 'unsigned':
                    await session.execute(
                        update(Album).where(Album.id == album_id).values(checker=None,
                                                                         unsigned_state='approve',
                                                                         approver_unsigned=employee_id)
                    )
                    await session.commit()
                    return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def reject(self, album_id, employee_id, state) -> bool:
        async with self.session_maker() as session:
            try:
                if state == 'unsigned':
                    await session.execute(
                        update(Album).where(Album.id == album_id).values(checker=None,
                                                                         unsigned_state='reject',
                                                                         approver_unsigned=employee_id)
                    )
                    await session.commit()
                    return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def set_title(self, album_id: int, title: str) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Album).where(Album.id == album_id).values(album_title=title)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def set_cover(self, album_id: int, cover) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Album).where(Album.id == album_id).values(album_cover=cover)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def update_unsigned_state(self, album_id: int, file_id) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Album).where(Album.id == album_id).values(unsigned_license=file_id,
                                                                     unsigned_state='process',
                                                                     sort_datetime=datetime.datetime.now())
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False
