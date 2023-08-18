from sqlalchemy import select, update, and_
from sqlalchemy.exc import SQLAlchemyError

from src.models.tables import TrackInfo, Track, PersonalData
from src.utils.enums import Status, FeatStatus


class TrackInfoHandler:

    def __init__(self, session_maker, logger):
        self.session_maker = session_maker
        self.logger = logger

    async def set_status_reject(self, track_id: int, edit_list: list, comment: str | None):
        async with self.session_maker() as session:
            try:
                result = dict.fromkeys(edit_list, None)
                result["status"] = Status.REJECT
                if comment:
                    result['comment'] = comment
                query = update(TrackInfo).where(TrackInfo.track_id == track_id).values(**result)
                await session.execute(query)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'отклонено': {e}")
                return False

    async def set_status_approve(self, track_id: int):
        async with self.session_maker() as session:
            try:
                query = update(TrackInfo).where(TrackInfo.track_id == track_id).values(status=Status.APPROVE)
                await session.execute(query)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def get_docs_by_id(self, track_id: int):
        async with self.session_maker() as session:
            try:
                query = select(TrackInfo).where(TrackInfo.track_id == track_id)
                result = await session.execute(query)
                result = result.scalar_one_or_none()
                if result is None:
                    result = TrackInfo(track_id=track_id)
                    session.add(result)
                    await session.commit()
                return result
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return None

    async def add_track_info(self, track_id: int, data: dict) -> bool:
        async with self.session_maker() as session:
            try:
                query = update(TrackInfo).where(TrackInfo.track_id == track_id).values(**data)
                await session.execute(query)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при добавлении нового трека: {e}")
                await session.rollback()
                return False

    async def get_docs_by_status(self, status: str) -> list | None:
        async with self.session_maker() as session:
            try:
                query = select(TrackInfo).where(TrackInfo.status == status)
                result = await session.execute(query)
                return result.scalars().all()
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return None

    async def update_track_info_feat(self, track_id: int, user_id: int) -> str:
        async with self.session_maker() as session:
            try:
                query = select(TrackInfo, Track, PersonalData).join_from(
                        TrackInfo, Track, TrackInfo.track_id == Track.id
                    ).join(
                        PersonalData, Track.user_id == PersonalData.tg_id
                    ).where(and_(
                        Track.id == track_id,
                        TrackInfo.feat_tg_id.is_(None),
                        Track.user_id != user_id
                    )).with_for_update()
                # Заблокировать строку и получить данные
                result = await session.execute(query)

                # Проверка результата перед распаковкой
                data = result.one_or_none()
                if not data:
                    return "Ошибка, нет возможности прикрепить данного пользователя."
                track_info, track, personal_data = data

                track_info.feat_tg_id = user_id

                if personal_data.all_passport_data == Status.APPROVE and personal_data.all_bank_data == Status.APPROVE:
                    track_info.status = Status.PROCESS
                    text_status = "трек отправлен на модерацию!"
                else:
                    track_info.feat_status = FeatStatus.WAIT_REG_FEAT
                    text_status = "пройдите верификацию, чтобы отправить трек на модерацию."
                await session.commit()

                return f"Данные обновлены, {text_status}"
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при обновлении информации о треке: {e}")
                await session.rollback()
                return "Ошибка на стороне сервера, обратитесь в службу поддержки.\n/support"
