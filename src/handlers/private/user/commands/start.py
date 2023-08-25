import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.deep_linking import decode_payload
from aiogram_dialog import DialogManager, StartMode
from sqlalchemy.ext.asyncio import async_sessionmaker
from structlog._log_levels import BoundLoggerFilteringAtDebug

from src.handlers.private.user.utils.check_user import check_user
from src.models.release import ReleaseHandler
from src.models.track_info import TrackInfoHandler
from src.models.user import UserHandler
from src.utils.fsm import RegNickname, StartMenu

router = Router()


@router.message(CommandStart(), flags={'chat_action': 'typing'})
async def cmd_start(msg: Message,
                    session_maker: async_sessionmaker,
                    database_logger: BoundLoggerFilteringAtDebug,
                    dialog_manager: DialogManager):
    user_handler = UserHandler(session_maker, database_logger)
    user = await user_handler.get_user_by_tg_id(msg.from_user.id)
    args = msg.text.split(" ")
    track = await ReleaseHandler(session_maker, database_logger).get_track_with_release(1)
    logging.info(track[0])
    if len(args) > 1:
        arg = decode_payload(args[1]).split("_")
        match arg:
            case "track", "feat", track_id_info:
                answer = await TrackInfoHandler(session_maker, database_logger). \
                    update_track_info_feat(int(track_id_info), msg.from_user.id)
                await msg.answer(text=answer)
    if await check_user(user, user_handler, dialog_manager, msg):
        await dialog_manager.start(StartMenu.start, mode=StartMode.RESET_STACK)
