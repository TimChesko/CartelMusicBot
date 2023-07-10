import logging

from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from src.dialogs.utils.common import on_start_copy_start_data
from src.models.personal_data import PersonalDataHandler
from src.models.tracks import TrackHandler
from src.utils.fsm import StartMenu, Listening, Library, PublicTrack, Service, PersonalDataFilling


async def get_data(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.middleware_data
    user_id = data['event_from_user'].id
    process = await TrackHandler(data['engine'], data['database_logger']).check_count_process_by_tg_id(user_id)
    logging.info(process)
    library = await TrackHandler(data['engine'], data['database_logger']).has_tracks_by_tg_id(user_id)
    user_data = not (
        await PersonalDataHandler(data['engine'], data['database_logger']).check_all_data_complete(user_id))
    tracks = await TrackHandler(data['engine'], data['database_logger']).check_chat_exists(user_id)
    return {
        'process_check': process,
        "library_check": library,
        'my_data_check': user_data,
        'track_check': tracks,
        'data': data
    }


start_menu = Dialog(
    Window(
        Const("Выберите нужную категорию"),
        Start(
            Const("Трек на прослушивание"),
            id='listening',
            state=Listening.start,
            when='process_check'
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
