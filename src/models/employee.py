from aiogram.types import Message
from sqlalchemy import select, and_, update
from sqlalchemy.exc import SQLAlchemyError

from src.database.process import DatabaseManager
from src.models.tables import Employee


class EmployeeHandler:

    def __init__(self, engine, logger):
        self.engine = engine
        self.logger = logger

    async def check_employee_by_tg_id(self, tg_id: int):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(Employee).where(and_(Employee.tg_id == tg_id))
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                return user
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return False

    async def get_privilege_by_tg_id(self, tg_id: int):
        async with DatabaseManager.create_session(self.engine) as session:
            try:
                query = select(Employee.privilege).where(and_(Employee.tg_id == tg_id))
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                return user
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return False
