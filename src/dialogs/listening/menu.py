from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const
from magic_filter import F

from src.dialogs.utils.buttons import BTN_CANCEL_BACK
from src.models.tracks import TrackHandler
from src.utils.fsm import Listening, ListeningNewTrack, ListeningEditTrack


async def tracks_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    process = await (TrackHandler(data['session_maker'], data['database_logger'])
                     .check_count_process_by_tg_id(data['event_from_user'].id))
    rejects = await (TrackHandler(data['session_maker'], data['database_logger'])
                     .has_reject_by_tg_id(data['event_from_user'].id))
    reject_tracks = await (TrackHandler(data['session_maker'], data['database_logger'])
                           .get_rejected_by_tg_id(data['event_from_user'].id))
    return {
        "rejects_check": rejects,
        'reject_tracks': reject_tracks,
        'process_check': process
    }


listening_menu = Dialog(
    Window(
        Const("🎧 Прослушивание\n\n"
              "❓ Первый этап выпуска ваших треков совместно с лейблом <b>CartelMusic</b>. "
              "На данным этапе вы присылаете свой трек на прослушивание модераторам, "
              "после чего ваш трек отправляется на стадию добавления информации о треке."),
        Const("\n🔰 Ограничение на количество треков: 3", when=F["process_check"].is_(False)),
        Const("Дождитесь проверки имеющихся треков на модерации", when=F["process_check"].is_(False)),
        Start(Const('❇️ Прислать трек'), state=ListeningNewTrack.start, id='listening_new_track', when='process_check',
              data="data"),
        Start(Const('❗️ Отклоненные'), state=ListeningEditTrack.start, id='listening_old_track', when='rejects_check'),
        BTN_CANCEL_BACK,
        state=Listening.start,
        getter=tracks_getter
    )
)
