import datetime

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.models.tables import Album


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
