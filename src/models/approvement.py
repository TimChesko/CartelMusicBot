import datetime

from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError

from src.models.tables import Track, TrackApprovement


class ApprovementHandler:

    def __init__(self, session_maker, logger):
        self.session_maker = session_maker
        self.logger = logger

    async def add_approve(self, employee_id: int, track_id: int, status: str = 'approve') -> bool:
        async with self.session_maker() as session:
            try:
                new_approval = TrackApprovement(track_id=track_id,
                                                employee_id=employee_id,
                                                datetime=datetime.datetime.now())
                session.add(new_approval)
                await session.execute(
                    update(Track).where(Track.id == track_id).values(status=status)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при добавлении нового пользователя: %s", e)
                await session.rollback()
                return False
