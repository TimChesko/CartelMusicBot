from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncEngine
from structlog._log_levels import BoundLoggerFilteringAtDebug

from src.models.user import UserHandler

router = Router()


@router.message(CommandStart(), flags={'chat_action': 'typing'})
async def cmd_start(msg: Message, engine: AsyncEngine, database_logger: BoundLoggerFilteringAtDebug):
    user = await UserHandler(engine, database_logger).get_all_by_tg_id(msg.from_user.id)
    if not user:
        user = await UserHandler(engine, database_logger).add_new_user(msg)
    database_logger.debug(user)
