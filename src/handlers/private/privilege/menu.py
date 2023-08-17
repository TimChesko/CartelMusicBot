from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode, ShowMode
from sqlalchemy.ext.asyncio import async_sessionmaker
from structlog._log_levels import BoundLoggerFilteringAtDebug

from src.models.employee import EmployeeHandler
from src.models.tables import Employee
from src.utils.fsm import AdminMenu, AdminRegistration

router = Router()


@router.message(Command('menu'), flags={'chat_action': 'typing'})
async def cmd_start(msg: Message,
                    session_maker: async_sessionmaker, database_logger: BoundLoggerFilteringAtDebug,
                    dialog_manager: DialogManager):
    await msg.delete()
    employee: Employee = await EmployeeHandler(session_maker, database_logger).check_employee_by_tg_id(msg.from_user.id)
    if employee and employee.fullname is None:
        await dialog_manager.start(AdminRegistration.first_name, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND)
    else:
        await dialog_manager.start(AdminMenu.start, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND)
