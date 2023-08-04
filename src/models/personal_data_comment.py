from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from src.models.tables import PersonalDataComments


class PersonalDataCommentsHandler:

    def __init__(self, session_maker, logger):
        self.session_maker = session_maker
        self.logger = logger

    async def set_comments(self, tg_id: int, data: dict):
        async with self.session_maker() as session:
            try:
                # Iterate over each item in data
                for column_name, comment in data.items():
                    new_comment = PersonalDataComments(tg_id=tg_id,
                                                       column_name=column_name,
                                                       comment=comment,
                                                       timestamp=datetime.now())
                    session.add(new_comment)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Error occurred during query execution: {e}")
                return None
