import datetime

from sqlalchemy import update, select, and_, or_, delete
from sqlalchemy.exc import SQLAlchemyError

from src.models.tables import Track, TrackApprovement, ListeningTemplates


class ListeningTemplatesHandler:

    def __init__(self, session_maker, logger):
        self.session_maker = session_maker
        self.logger = logger

    async def add_reject(self, name, content) -> bool:
        async with self.session_maker() as session:
            try:
                new_user = ListeningTemplates(type='reject', name=name, content=content)
                session.add(new_user)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при добавлении нового пользователя: %s", e)
                await session.rollback()
                return False

    async def delete_template(self, num_id: int) -> bool:
        async with self.session_maker() as session:
            try:
                await session.execute(
                    delete(ListeningTemplates).where(ListeningTemplates.id == num_id)
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при удалении шаблона: {e}")
                return False

    async def get_all_all(self, type_name) -> str | bool:
        async with self.session_maker() as session:
            try:
                query = select(ListeningTemplates.id, ListeningTemplates.name).where(
                    ListeningTemplates.type == type_name)
                result = await session.execute(query)
                reason = result.all()
                return reason
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_all_scalar(self, type_name, num_id=None) -> str | bool:
        async with self.session_maker() as session:
            try:
                if num_id is None:
                    query = select(ListeningTemplates).where(ListeningTemplates.type == type_name)
                else:
                    query = select(ListeningTemplates).where(ListeningTemplates.id == num_id)
                result = await session.execute(query)
                reason = result.scalar_one_or_none()
                return reason
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def get_approve_reason(self, type_name) -> str | bool:
        async with self.session_maker() as session:
            try:
                query = select(ListeningTemplates.content).where(ListeningTemplates.type == type_name)
                result = await session.execute(query)
                reason = result.scalar_one_or_none()
                return reason
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при выполнении запроса: {e}")
                return False

    async def update_content(self, type: str, content: str, num_id=None):
        async with self.session_maker() as session:
            try:
                if num_id is None:
                    await session.execute(
                        update(ListeningTemplates).where(ListeningTemplates.type == type).values(content=content)
                    )
                else:
                    await session.execute(
                        update(ListeningTemplates).where(ListeningTemplates.id == num_id).values(content=content)
                    )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False

    async def update_name(self, type: str, name: str, id=None):
        async with self.session_maker() as session:
            try:
                if id is None:
                    await session.execute(
                        update(ListeningTemplates).where(ListeningTemplates.type == type).values(name=name)
                    )
                else:
                    await session.execute(
                        update(ListeningTemplates).where(ListeningTemplates.id == id).values(name=name)
                    )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error(f"Ошибка при установке трека в состояние 'в процессе': {e}")
                return False
