from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.kbd import Start, Button
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.utils.common import on_start_copy_start_data
from src.models.personal_data import PersonalDataHandler
from src.models.tracks import TrackHandler
from src.utils.fsm import StartMenu, Listening, Profile, \
    PersonalData, MyStudio, ReleaseTrack


async def get_data(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    user_id = dialog_manager.event.from_user.id
    library = await TrackHandler(data['session_maker'], data['database_logger']).has_tracks_by_tg_id(user_id)
    tracks = await TrackHandler(data['session_maker'], data['database_logger']).check_chat_exists(user_id)
    personal_data = await PersonalDataHandler(data['session_maker'], data['database_logger']). \
        get_all_by_tg(user_id)
    return {
        "library_check": library,
        'verif_check': all((personal_data.all_passport_data == 'approve', personal_data.all_bank_data == 'approve')),
        'track_check': tracks,
        'data': data,
        "text": "🙎‍♂️ Профиль" if personal_data.all_passport_data and personal_data.all_bank_data
        else "✅ Пройти верификацию"
    }


async def start_profile(_, __, manager: DialogManager):
    data = manager.middleware_data
    user_id = manager.event.from_user.id
    personal_data = await PersonalDataHandler(data['session_maker'], data['database_logger']). \
        get_all_by_tg(user_id)
    if personal_data.confirm_use_personal_data:
        await manager.start(state=Profile.menu)
    else:
        await manager.start(state=PersonalData.confirm)


start_menu = Dialog(
    Window(
        Const("Выберите нужную категорию"),
        Start(
            Const("🎙 Трек на прослушивание"),
            id='listening',
            state=Listening.start,
        ),
        Start(
            Const("💠 Моя студия"),
            id='my_studio',
            state=MyStudio.menu,
            when='verif_check'
        ),
        Start(
            Const("📨 Выпустить трек в продакшн"),
            id='public_track',
            state=ReleaseTrack.list,
            when='verif_check'
        ),
        Button(
            Format("{text}"),
            id='profile',
            on_click=start_profile,
            when='track_check'
        ),
        state=StartMenu.start,
        getter=get_data
    ),
    on_start=on_start_copy_start_data
)
