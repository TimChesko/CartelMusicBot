import logging

from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.deep_linking import decode_payload
from aiogram_dialog import DialogManager, StartMode, ShowMode
from sqlalchemy.ext.asyncio import AsyncEngine
from structlog._log_levels import BoundLoggerFilteringAtDebug

from src.data import config
from src.keyboards.inline.listening import markup_answerer_name
from src.models.tracks import TrackHandler
from src.models.user import UserHandler
from src.utils.fsm import RegNickname, StartMenu, RejectAnswer

router = Router()


@router.message(CommandStart(), flags={'chat_action': 'typing'})
async def cmd_start(msg: Message,
                    engine: AsyncEngine, database_logger: BoundLoggerFilteringAtDebug,
                    dialog_manager: DialogManager, bot: Bot):
    user = await UserHandler(engine, database_logger).check_user_by_tg_id(msg.from_user.id)
    listening_chat = config.CHATS_BACKUP[0]
    args = msg.text.split(' ')
    if not user:
        await UserHandler(engine, database_logger).add_new_user(msg)
        user = await UserHandler(engine, database_logger).check_user_by_tg_id(msg.from_user.id)
    if user.nickname is None:
        await dialog_manager.start(RegNickname.nickname, mode=StartMode.RESET_STACK)
    if len(args) == 2:
        logging.info(args[1])
        decode = decode_payload(args[1]).split('_')
        logging.info(decode)
        msg_id = await TrackHandler(engine, database_logger).get_task_msg_id_by_track_id(int(decode[1]))
        await bot.edit_message_reply_markup(listening_chat, msg_id,
                                            reply_markup=markup_answerer_name(msg.from_user.username))
        await dialog_manager.start(state=RejectAnswer.start, mode=StartMode.RESET_STACK, data={'track_id': decode[1],
                                                                                               'state': decode[0],
                                                                                               'admin_id': msg.from_user.id,
                                                                                               'msg_id': msg_id})
    elif user and user.nickname is not None:
        await msg.delete()
        await dialog_manager.start(StartMenu.start, mode=StartMode.RESET_STACK)
