from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from sqlalchemy.ext.asyncio import AsyncEngine
from structlog._log_levels import BoundLoggerFilteringAtDebug

from src.models.user import UserHandler
from src.utils.fsm import RegNickname, StartMenu

router = Router()


@router.message(CommandStart(), flags={'chat_action': 'typing'})
async def cmd_start(msg: Message, engine: AsyncEngine, database_logger: BoundLoggerFilteringAtDebug,
                    dialog_manager: DialogManager):
    user = await UserHandler(engine, database_logger).get_nicknames_by_tg_id(msg.from_user.id)
    if not user:
        await UserHandler(engine, database_logger).add_new_user(msg)
        await dialog_manager.start(RegNickname.nickname, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(StartMenu.start, mode=StartMode.RESET_STACK)
