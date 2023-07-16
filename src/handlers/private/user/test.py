from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncEngine
from structlog._log_levels import BoundLoggerFilteringAtDebug

router = Router()


@router.message(Command(commands="test"), flags={'chat_action': 'typing'})
async def cmd_start(msg: Message,
                    engine: AsyncEngine,
                    database_logger: BoundLoggerFilteringAtDebug,
                    dialog_manager: DialogManager):
    pass
