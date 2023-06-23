from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, StartMode, Dialog, Window
from aiogram_dialog.widgets.kbd import Start, Button
from aiogram_dialog.widgets.text import Const
from sqlalchemy.ext.asyncio import AsyncEngine
from structlog._log_levels import BoundLoggerFilteringAtDebug

from src.handlers.private.user.dialogs.utils.common import on_start_copy_start_data
from src.models.chats import ChatsHandler
from src.models.tables import User
from src.models.user import UserHandler
from src.utils.fsm import RegNickname, StartMenu, Listening, Library, PublicTrack, Service, ListeningNewTrack, PersonalDataFilling

router = Router()


@router.message(CommandStart(), flags={'chat_action': 'typing'})
async def cmd_start(msg: Message, engine: AsyncEngine, database_logger: BoundLoggerFilteringAtDebug,
                    dialog_manager: DialogManager):
    user = await UserHandler(engine, database_logger).get_all_by_tg_id(msg.from_user.id)
    if not user:
        await UserHandler(engine, database_logger).add_new_user(msg)
    if user.nickname is None:
        await dialog_manager.start(RegNickname.nickname, mode=StartMode.RESET_STACK)
    else:
        await dialog_manager.start(StartMenu.start, mode=StartMode.RESET_STACK)


async def get_data(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.middleware_data
    user_id = data['event_from_user'].id
    library = await ChatsHandler(data['engine'], data['database_logger']).has_chats_by_tg_id(user_id)
    user_data = not (await UserHandler(data['engine'], data['database_logger']).check_all_data_complete(user_id))
    tracks = await ChatsHandler(data['engine'], data['database_logger']).check_chat_exists(user_id)
    return {
        "library_check": library,
        'my_data_check': user_data,
        'track_check': tracks,
        'data': data
    }


async def check_track(callback: CallbackQuery, _, dialog_manager: DialogManager, ):
    data = dialog_manager.middleware_data
    if await ChatsHandler(data['engine'], data['database_logger']).has_reject_by_tg_id(callback.from_user.id, 1):
        await dialog_manager.start(Listening.start, data=dialog_manager.dialog_data)
    else:
        await dialog_manager.start(ListeningNewTrack.track, data=dialog_manager.dialog_data)


start_menu = Dialog(
    Window(
        Const("Выберете нужную категорию"),
        Button(
            Const("Трек на прослушивание"),
            id='listening',
            on_click=check_track
        ),
        Start(
            Const("Мои треки"),
            id='library',
            state=Library.start,
            when='library_check'
        ),
        Start(
            Const("Заполнить личные данные"),
            id='my_data',
            state=PersonalDataFilling.start,
            when='my_data_check'
        ),
        Start(
            Const("Выпустить трек в продакшн"),
            id='public_track',
            state=PublicTrack.list,
            when='track_check'
        ),
        Start(
            Const("Услуги"),
            id='services',
            state=Service.menu,
        ),
        state=StartMenu.start,
        getter=get_data
    ),
    on_start=on_start_copy_start_data
)
