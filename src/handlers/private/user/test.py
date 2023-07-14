from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from sqlalchemy.ext.asyncio import AsyncEngine
from structlog._log_levels import BoundLoggerFilteringAtDebug

from src.models.user import UserHandler
from src.utils.fsm import RegNickname, StartMenu, Profile, DialogInput

router = Router()


@router.message(Command(commands="test"), flags={'chat_action': 'typing'})
async def cmd_start(msg: Message,
                    engine: AsyncEngine,
                    database_logger: BoundLoggerFilteringAtDebug,
                    dialog_manager: DialogManager):
    await dialog_manager.start(state=DialogInput.text, mode=StartMode.RESET_STACK)
