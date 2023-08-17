from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.deep_linking import decode_payload
from aiogram_dialog import DialogManager, StartMode
from sqlalchemy.ext.asyncio import async_sessionmaker
from structlog._log_levels import BoundLoggerFilteringAtDebug

from src.handlers.private.user.utils.check_user import check_user
from src.models.track_info import TrackInfoHandler
from src.models.user import UserHandler
from src.utils.fsm import RegNickname, StartMenu

router = Router()


@router.message(Command(commands=["info"]), flags={'chat_action': 'typing'})
async def cmd_bot_info(msg: Message,
                       session_maker: async_sessionmaker,
                       database_logger: BoundLoggerFilteringAtDebug,
                       dialog_manager: DialogManager):
    user_handler = UserHandler(session_maker, database_logger)
    user = await user_handler.get_user_by_tg_id(msg.from_user.id)
    if await check_user(user, user_handler, dialog_manager, msg):
        await dialog_manager.start(StartMenu.start, mode=StartMode.RESET_STACK)
