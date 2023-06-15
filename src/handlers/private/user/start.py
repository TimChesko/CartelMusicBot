import logging

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode, Dialog, Window, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const
from sqlalchemy.ext.asyncio import AsyncEngine
from structlog._log_levels import BoundLoggerFilteringAtDebug

from src.models.chats import ChatsHandler
from src.models.tables import User
from src.models.user import UserHandler
from src.utils.fsm import RegNickname, StartMenu, Listening, Library, PublicTrack, Service, MyData

router = Router()


@router.message(CommandStart(), flags={'chat_action': 'typing'})
async def cmd_start(msg: Message, engine: AsyncEngine, database_logger: BoundLoggerFilteringAtDebug,
                    dialog_manager: DialogManager):
    user = await UserHandler(engine, database_logger).get_all_by_tg_id(msg.from_user.id)
    if not user:
        user = await UserHandler(engine, database_logger).add_new_user(msg)
    if not user.nickname:
        await dialog_manager.start(RegNickname.nickname, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(StartMenu.start, mode=StartMode.RESET_STACK)


async def get_data(dialog_manager: DialogManager, **kwargs):
    data = (await dialog_manager.load_data())['middleware_data']
    user_id = data['event_from_user'].id
    library = await ChatsHandler(data['engine'], data['database_logger']).has_chats_by_tg_id(user_id)
    user_data = not (await UserHandler(data['engine'], data['database_logger']).check_all_data_complete(user_id))
    tracks = await ChatsHandler(data['engine'], data['database_logger']).check_chat_exists(user_id)
    return {
        "library_check": library,
        'my_data_check': user_data,
        'track_check': tracks
    }


start_menu = Dialog(
    Window(
        Const("Выберете нужную категорию"),
        Start(
            Const("Трек на прослушивание"), id='listening', state=Listening.start
        ),
        Start(
            Const("Мои треки"), id='library', state=Library.start, when='library_check'
        ),
        Start(
            Const("Заполнить личные данные"), id='my_data', state=MyData.start,
            when='my_data_check'
        ),
        Start(
            Const("Выпустить трек в продакшн"), id='public_track', state=PublicTrack.list,
            when='track_check'
        ),
        Start(
            Const("Услуги"), id='services', state=Service.menu
        ),
        state=StartMenu.start,
        getter=get_data,
    )
)
