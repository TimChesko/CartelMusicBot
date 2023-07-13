import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.deep_linking import decode_payload
from aiogram_dialog import DialogManager, StartMode, ShowMode
from sqlalchemy.ext.asyncio import AsyncEngine
from structlog._log_levels import BoundLoggerFilteringAtDebug

from src.models.user import UserHandler
from src.utils.fsm import RegNickname, StartMenu, RejectAnswer

router = Router()


@router.message(CommandStart(), flags={'chat_action': 'typing'})
async def cmd_start(msg: Message,
                    engine: AsyncEngine, database_logger: BoundLoggerFilteringAtDebug,
                    dialog_manager: DialogManager):
    user = await UserHandler(engine, database_logger).get_nicknames_by_tg_id(msg.from_user.id)
    if not user:
        await UserHandler(engine, database_logger).add_new_user(msg)
        await dialog_manager.start(RegNickname.nickname, mode=StartMode.RESET_STACK)
    args = msg.text.split(' ')
    logging.info(args)
    if len(args) == 2:
        logging.info(args[1])
        decode = decode_payload(args[1])
        await dialog_manager.start(state=RejectAnswer.start, mode=StartMode.RESET_STACK, data={'track_id': decode,
                                                                                               'admin_id': msg.from_user.id})
    else:
        await msg.delete()
        logging.info(msg.message_id)
        await dialog_manager.start(StartMenu.start, mode=StartMode.RESET_STACK, show_mode=ShowMode.SEND)
