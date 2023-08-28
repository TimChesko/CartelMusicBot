import datetime

from sqlalchemy import select, update, delete, asc, and_, or_
from sqlalchemy.exc import SQLAlchemyError

from src.models.tables import Release, Track, User, TrackInfo
from src.utils.enums import Status


# noinspection PyTypeChecker
class ReleaseHandler:

    def __init__(self, session_maker, logger):
        self.session_maker = session_maker
        self.logger = logger

    async def add_new_release(self, user_id: int) -> bool:
        async with self.session_maker() as session:
            try:
                new_track = Release(user_id=user_id)
                session.add(new_track)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при добавлении нового трека: {e}")
                await session.rollback()
                return False

    async def get_release_by_user_id(self, user_id):
        async with self.session_maker() as session:
            try:
                result = await session.execute(
                    select(Release.id, Release.release_title).where(and_(Release.user_id == user_id,
                                                                         or_(Release.mail_track_status == Status.REJECT,
                                                                             Release.mail_track_status == Status.PROCESS,
                                                                             Release.mail_track_status == None))))
                track_info = result.all()
                return track_info
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_unsigned_state(self, state):
        async with self.session_maker() as session:
            try:
                result = await session.execute(
                    select(Release).where(Release.unsigned_status == state).order_by(
                        asc(Release.date_last_edit))
                )
                track_info = result.scalars().all()
                return track_info
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_signed_state(self, state):
        async with self.session_maker() as session:
            try:
                result = await session.execute(
                    select(Release).where(Release.signed_status == state).order_by(
                        asc(Release.date_last_edit))
                )
                track_info = result.scalars().all()
                return track_info
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_mail_state(self, state):
        async with self.session_maker() as session:
            try:
                result = await session.execute(
                    select(Release).where(Release.mail_track_status == state).order_by(
                        asc(Release.date_last_edit))
                )
                track_info = result.scalars().all()
                return track_info
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_release_scalar(self, release_id) -> Release:
        async with self.session_maker() as session:
            try:
                release = await session.execute(select(Release).where(Release.id == release_id))
                release_info = release.scalar_one_or_none()
                tracks = await session.execute(select(Track).where(Track.release_id == release_id))
                tracks_info = tracks.scalars().all()
                return release_info, tracks_info
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_track_with_release(self, release_id) -> list[TrackInfo]:
        async with self.session_maker() as session:
            try:
                release_info = await session.execute(
                    select(Release).where(Release.id == release_id)
                )
                release = release_info.scalar_one_or_none()
                tracks = await session.execute(
                    select(TrackInfo)
                    .join(Track)
                    .where(Track.release_id == release_id)
                )
                tracks_info = tracks.scalars().all()
                return tracks_info, release
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def delete_release_id_from_tracks(self, release_id) -> Release:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Track).where(Track.release_id == release_id).values(release_id=None)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def delete_release(self, release_id) -> Release:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Track).where(Track.release_id == release_id).values(release_id=None)
                )
                await session.execute(
                    delete(Release).where(Release.id == release_id)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_tracks_and_personal_data(self, tg_id: int, release_id: int):
        async with self.session_maker() as session:
            try:
                user = await session.execute(select(User).where(User.tg_id == tg_id))
                user = user.scalar_one()
                release = await session.execute(select(Release).where(Release.id == release_id))
                release = release.scalar_one()
                tracks = await session.execute(select(Track).where(Track.release_id == release_id))
                tracks = tracks.scalars().all()
                return user, tracks, release
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_release_lvl1_info(self, release_id: int):
        async with self.session_maker() as session:
            try:
                query = select(Release, User).join(User).where(Release.id == release_id)
                result = await session.execute(query)
                tracks = result.first()
                return tracks
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_release(self, release_id: int) -> Release:
        async with self.session_maker() as session:
            try:
                query = select(Release).where(Release.id == release_id)
                result = await session.execute(query)
                tracks = result.scalar()
                return tracks
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def set_task_state(self, release_id, employee_id=None) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Release).where(Release.id == release_id).values(checker_id=employee_id)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при добавления checker_id': {e}")
                return False

    async def approve(self, release_id, employee_id, state) -> bool:
        async with self.session_maker() as session:
            try:
                if state == 'unsigned':
                    await session.execute(
                        update(Release).where(Release.id == release_id).values(checker_id=None,
                                                                               unsigned_status=Status.APPROVE)
                    )
                    await session.commit()
                    return True
                if state == 'signed':
                    await session.execute(
                        update(Release).where(Release.id == release_id).values(checker_id=None,
                                                                               signed_status=Status.APPROVE)
                    )
                    await session.commit()
                    return True
                if state == 'mail':
                    await session.execute(
                        update(Release).where(Release.id == release_id).values(checker_id=None,
                                                                               mail_track_status=Status.APPROVE)
                    )
                    await session.commit()
                    return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def reject(self, release_id, employee_id, state) -> bool:
        async with self.session_maker() as session:
            try:
                if state == 'unsigned':
                    await session.execute(
                        update(Release).where(Release.id == release_id).values(checker_id=None,
                                                                               unsigned_status=Status.REJECT)
                    )
                    await session.commit()
                    return True
                if state == 'signed':
                    await session.execute(
                        update(Release).where(Release.id == release_id).values(checker_id=None,
                                                                               signed_status=Status.REJECT)
                    )
                    await session.commit()
                    return True
                if state == 'mail':
                    await session.execute(
                        update(Release).where(Release.id == release_id).values(checker_id=None,
                                                                               mail_track_status=Status.REJECT)
                    )
                    await session.commit()
                    return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def set_title(self, release_id: int, title: str) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Release).where(Release.id == release_id).values(release_title=title)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def set_cover(self, release_id: int, cover) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Release).where(Release.id == release_id).values(release_cover=cover)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def set_ld(self, release_id: int, ld) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Release).where(Release.id == release_id).values(signed_license=ld)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def set_mail_track(self, release_id: int, photo) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Release).where(Release.id == release_id).values(mail_track_photo=photo)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def update_unsigned_state(self, release_id: int, file_id) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Release).where(Release.id == release_id).values(unsigned_license=file_id,
                                                                           unsigned_status=Status.PROCESS,
                                                                           date_last_edit=datetime.datetime.utcnow())
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def add_unsigned_feat(self, release: Release, file_id) -> bool:
        async with self.session_maker() as session:
            try:
                new_feat = Release(parent_release=release.id,
                                   release_cover=release.release_cover,
                                   release_title=release.release_title,
                                   unsigned_license=file_id,
                                   date_last_edit=datetime.datetime.utcnow())
                session.add(new_feat)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def update_signed_state(self, release_id: int) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Release).where(Release.id == release_id).values(signed_status=Status.PROCESS,
                                                                           date_last_edit=datetime.datetime.utcnow())
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def update_mail_state(self, release_id: int) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    update(Release).where(Release.id == release_id).values(mail_track_status=Status.PROCESS,
                                                                           date_last_edit=datetime.datetime.utcnow())
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False
