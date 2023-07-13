from aiogram_dialog import DialogManager, Dialog, Window, ShowMode
from aiogram_dialog.widgets.kbd import Start, Button
from aiogram_dialog.widgets.text import Const

from src.dialogs.utils.common import on_start_copy_start_data
from src.models.personal_data import PersonalDataHandler
from src.models.tracks import TrackHandler
from src.utils.fsm import StartMenu, Listening, PublicTrack, Service, MyTracks, Profile, \
    PersonalData


async def get_data(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.middleware_data
    user_id = data['event_from_user'].id
    library = await TrackHandler(data['engine'], data['database_logger']).has_tracks_by_tg_id(user_id)
    tracks = await TrackHandler(data['engine'], data['database_logger']).check_chat_exists(user_id)
    return {
        "library_check": library,
        'track_check': tracks,
        'data': data
    }


async def start_listening(_, __, manager: DialogManager):
    manager.show_mode = ShowMode.EDIT


async def start_profile(_, __, manager: DialogManager):
    data = manager.middleware_data
    user_id = data['event_from_user'].id
    personal_data = await PersonalDataHandler(data['engine'], data['database_logger']).get_personal_data_confirm(
        user_id)
    if personal_data:
        await manager.start(state=Profile.menu)
    else:
        await manager.start(state=PersonalData.confirm)


start_menu = Dialog(
    Window(
        Const("Выберите нужную категорию"),
        Start(
            Const("Трек на прослушивание"),
            id='listening',
            state=Listening.start,
            on_click=start_listening
        ),
        Start(
            Const("Мои треки"),
            id='library',
            state=MyTracks.start,
            when='library_check'
        ),
        Start(
            Const("Выпустить трек в продакшн"),
            id='public_track',
            state=PublicTrack.list,
            when='track_check'
        ),
        Button(
            Const("Профиль"),
            id='profile',
            on_click=start_profile
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
