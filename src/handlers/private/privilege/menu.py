from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode, ShowMode
from sqlalchemy.ext.asyncio import async_sessionmaker
from structlog._log_levels import BoundLoggerFilteringAtDebug

from src.models.user import UserHandler
from src.utils.fsm import AdminMenu

router = Router()


@router.message(Command('menu'), flags={'chat_action': 'typing'})
async def cmd_start(msg: Message,
                    session_maker: async_sessionmaker, database_logger: BoundLoggerFilteringAtDebug,
                    dialog_manager: DialogManager, bot: Bot):
    await msg.delete()
    user = await UserHandler(session_maker, database_logger).check_user_by_tg_id(msg.from_user.id)
    if not user:
        await UserHandler(session_maker, database_logger).add_new_user(msg)
    await dialog_manager.start(AdminMenu.start, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND)