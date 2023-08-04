from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.models.tables import TrackInfo, Track, PersonalData


class TrackInfoHandler:

    def __init__(self, session_maker, logger):
        self.session_maker = session_maker
        self.logger = logger

    async def get_docs_by_status(self, status: str) -> list | None:
        async with self.session_maker() as session:
            try:
                query = select(TrackInfo).where(TrackInfo.status == status)
                result = await session.execute(query)
                docs = result.scalars().all()
                return docs
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return None

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
