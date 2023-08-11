import datetime

from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError

from src.models.tables import Track, TrackApprovement


class ApprovementHandler:

    def __init__(self, session_maker, logger):
        self.session_maker = session_maker
        self.logger = logger

    async def add_reject(self, employee_id: int, track_id: int, template_id: int) -> bool:
        async with self.session_maker() as session:
            try:
                new_rejection = TrackApprovement(track_id=track_id,
                                                 employee_id=employee_id,
                                                 datetime=datetime.datetime.now(),
                                                 template_id=template_id)
                session.add(new_rejection)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при добавлении нового пользователя: %s", e)
                await session.rollback()
                return False

    async def add_custom_reject(self, employee_id: int, track_id: int, reason: str) -> bool:
        async with self.session_maker() as session:
            try:
                new_rejection = TrackApprovement(track_id=track_id,
                                                 employee_id=employee_id,
                                                 datetime=datetime.datetime.now(),
                                                 reason=reason)
                session.add(new_rejection)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при добавлении нового пользователя: %s", e)
                await session.rollback()
                return False
