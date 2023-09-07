from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.kbd import Start, Button
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.utils.common import on_start_copy_start_data
from src.models.personal_data import PersonalDataHandler
from src.models.tracks import TrackHandler
from src.utils.enums import Status
from src.utils.fsm import StartMenu, Listening, Profile, \
    PersonalData, MyStudio, ReleaseTrack, ReleaseFeat


async def get_data(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    user_id = data['event_from_user'].id
    track_handler = TrackHandler(data['session_maker'], data['database_logger'])
    library = await track_handler.has_tracks_by_tg_id(user_id)
    tracks = await track_handler.check_tracks_exists(user_id)
    tracks_feat = await track_handler.check_feat_exists(user_id)
    personal_data = await PersonalDataHandler(data['session_maker'], data['database_logger']). \
        get_all_by_tg(user_id)
    return {
        "library_check": library,
        'verif_check': personal_data.all_passport_data == Status.APPROVE and personal_data.all_bank_data == Status.APPROVE,
        'track_check': tracks or tracks_feat,
        "has_btn": "\nВыберете категорию:" if tracks else "",
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
        Const("""🏠 <b>Главное меню</b>
        
🚀 Узнать все возможности бота - /info
👨‍🚀 Поддержка - @CartelMusicSupport
❓ Частые вопросы - /help"""),
        Format("{has_btn}"),
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
            Const("📨 Личный продакшн"),
            id='public_track',
            state=ReleaseTrack.list,
            when='verif_check'
        ),
        Start(
            Const("👨‍👦‍👦Совместный продакшн"),
            id='feats',
            state=ReleaseFeat.list,
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
