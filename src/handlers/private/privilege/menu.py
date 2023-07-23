from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode, ShowMode
from sqlalchemy.ext.asyncio import async_sessionmaker
from structlog._log_levels import BoundLoggerFilteringAtDebug

from src.models.employee import EmployeeHandler
from src.models.tables import Employee, User
from src.models.user import UserHandler
from src.utils.fsm import AdminMenu, AdminRegistration

router = Router()


@router.message(Command('menu'), flags={'chat_action': 'typing'})
async def cmd_start(msg: Message,
                    session_maker: async_sessionmaker, database_logger: BoundLoggerFilteringAtDebug,
                    dialog_manager: DialogManager):
    await msg.delete()
    user: User = await UserHandler(session_maker, database_logger).check_user_by_tg_id(msg.from_user.id)
    if not user:
        await UserHandler(session_maker, database_logger).add_new_user(msg)
    employee: Employee = await EmployeeHandler(session_maker, database_logger).check_employee_by_tg_id(msg.from_user.id)
    if any(name is None for name in (employee.first_name, employee.middle_name, employee.surname)):
        await dialog_manager.start(AdminRegistration.first_name, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND)
    else:
        await dialog_manager.start(AdminMenu.start, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND)