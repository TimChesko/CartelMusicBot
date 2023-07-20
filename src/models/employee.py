from datetime import datetime

from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError

from src.data import config
from src.models.tables import Employee, User


class EmployeeHandler:

    def __init__(self, session_maker, logger):
        self.session_maker = session_maker
        self.logger = logger

    async def add_new_employee(self, user_id, privilege) -> bool:
        async with self.session_maker() as session:
            try:
                new_user = Employee(tg_id=int(user_id), privilege=privilege, add_date=datetime.now())
                session.add(new_user)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при добавлении нового пользователя: %s", e)
                await session.rollback()
                return False

    async def check_employee_by_tg_id(self, tg_id: int):
        async with self.session_maker() as session:
            try:
                query = select(Employee).where(and_(Employee.tg_id == tg_id, Employee.state != 'fired'))
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                return user
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return False

    async def get_privilege_by_tg_id(self, tg_id: int):
        async with self.session_maker() as session:
            try:
                query = select(Employee.privilege).where(and_(Employee.tg_id == tg_id))
                result = await session.execute(query)
                user = result.scalar_one_or_none()
                return user
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return False

    async def set_privilege(self, user_id: int, new_privilege: str) -> bool:
        async with self.session_maker() as session:
            try:
                employee = await session.get(Employee, user_id)
                if employee:
                    employee.privilege = new_privilege
                    await session.commit()
                    return True
                else:
                    self.logger.error(f"Пользователь с tg_id {user_id} не найден, set_privilege")
                    return False
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при добавлении нового пользователя: %s", e)
                await session.rollback()
                return False

    async def get_privilege_by_filter(self, privilege: str | None = None):
        async with self.session_maker() as session:
            try:
                if privilege in config.PRIVILEGES:
                    query = select(Employee.tg_id, User.tg_username, Employee.first_name, Employee.surname).join(
                        User).where(and_(Employee.privilege == privilege, Employee.state != 'fired'))
                elif privilege == 'regs' or privilege == 'fired':
                    query = select(Employee.tg_id, User.tg_username, Employee.first_name, Employee.surname).join(
                        User).where(Employee.state == privilege)
                else:
                    query = select(Employee.tg_id, User.tg_username, Employee.first_name, Employee.surname).join(
                        User).where(Employee.state != 'fired')
                result = await session.execute(query)
                employee = result.all()
                return employee
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return False

    async def get_privileges_by_filter(self, privilege: str | None = None):
        async with self.session_maker() as session:
            try:
                if privilege in config.PRIVILEGES:
                    query = select(Employee).join(
                        User).where(Employee.privilege == privilege)
                elif privilege == 'regs':
                    query = select(Employee).join(
                        User).where(Employee.state == privilege)
                else:
                    query = select(Employee).join(User)
                result = await session.execute(query)
                employee = result.all()
                return employee
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return False

    async def get_dialog_info_by_tg_id(self, tg_id: int):
        async with self.session_maker() as session:
            try:
                query = select(Employee.first_name,
                               Employee.surname,
                               Employee.middle_name,
                               Employee.privilege,
                               Employee.state,
                               Employee.add_date,
                               Employee.fired_date,
                               Employee.recovery_date).where(Employee.tg_id == tg_id)
                result = await session.execute(query)
                employee = result.one()
                return employee
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return False

    async def get_all_by_tg_id(self, tg_id: int):
        async with self.session_maker() as session:
            try:
                query = select(Employee).where(Employee.tg_id == tg_id)
                result = await session.execute(query)
                employee = result.one()
                return employee
            except SQLAlchemyError as e:
                self.logger.error("Ошибка при выполнении запроса: %s", e)
                return False
