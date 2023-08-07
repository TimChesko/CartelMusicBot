import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.deep_linking import decode_payload
from aiogram_dialog import DialogManager, StartMode
from sqlalchemy.ext.asyncio import async_sessionmaker
from structlog._log_levels import BoundLoggerFilteringAtDebug

from src.models.track_info import TrackInfoHandler
from src.models.user import UserHandler
from src.utils.fsm import RegNickname, StartMenu

router = Router()


@router.message(CommandStart(), flags={'chat_action': 'typing'})
async def cmd_start(msg: Message,
                    session_maker: async_sessionmaker,
                    database_logger: BoundLoggerFilteringAtDebug,
                    dialog_manager: DialogManager):
    user = await UserHandler(session_maker, database_logger).get_user_by_tg_id(msg.from_user.id)
    args = msg.text.split(" ")
    if len(args) > 1:
        arg = decode_payload(args[1]).split("_")
        match arg:
            case "track", "feat", track_id_info:
                answer = await TrackInfoHandler(session_maker, database_logger). \
                    update_track_info_feat(int(track_id_info), msg.from_user.id)
                await msg.answer(text=answer)
    if not user:
        await UserHandler(session_maker, database_logger).add_new_user(msg)
        user = await UserHandler(session_maker, database_logger).get_user_by_tg_id(msg.from_user.id)
    await msg.delete()
    if user.nickname is None:
        await dialog_manager.start(RegNickname.nickname, mode=StartMode.RESET_STACK)
    elif user and user.nickname is not None:
        await dialog_manager.start(StartMenu.start, mode=StartMode.RESET_STACK)
