from aiogram_dialog import DialogManager, Dialog, Window, ShowMode, StartMode
from aiogram_dialog.widgets.kbd import Start, Button
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.utils.common import on_start_copy_start_data
from src.models.personal_data import PersonalDataHandler
from src.models.track import TrackHandler
from src.utils.fsm import StartMenu, Listening, Profile, \
    PersonalData, MyStudio, ReleaseTrack


async def get_data(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.middleware_data
    user_id = data['event_from_user'].id
    library = await TrackHandler(data['session_maker'], data['database_logger']).has_tracks_by_tg_id(user_id)
    tracks = await TrackHandler(data['session_maker'], data['database_logger']).check_chat_exists(user_id)
    passport, bank = await PersonalDataHandler(data['session_maker'], data['database_logger']).\
        get_all_data_status(user_id)
    return {
        "library_check": library,
        'track_check': tracks,
        'data': data,
        "text": "Профиль" if passport and bank else "Пройти верификацию"
    }


async def start_listening(_, __, manager: DialogManager):
    manager.show_mode = ShowMode.EDIT


async def start_profile(_, __, manager: DialogManager):
    data = manager.middleware_data
    user_id = data['event_from_user'].id
    personal_data = await PersonalDataHandler(data['session_maker'], data['database_logger']).\
        get_personal_data_confirm(user_id)
    if personal_data:
        await manager.start(state=Profile.menu, mode=StartMode.NORMAL)
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
            Const("Мои студия"),
            id='my_studio',
            state=MyStudio.menu
        ),
        Start(
            Const("Выпустить трек в продакшн"),
            id='public_track',
            state=ReleaseTrack.list
        ),
        Button(
            Format("{text}"),
            id='profile',
            on_click=start_profile
        ),
        state=StartMenu.start,
        getter=get_data
    ),
    on_start=on_start_copy_start_data
)
