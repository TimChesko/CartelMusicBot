from _operator import itemgetter

from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Start, ScrollingGroup, Select, Cancel, Button, Back, Row, Next
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.tracks.listening import on_item_selected, tracks_getter, set_music_file_for_edit, \
    other_type_handler_audio, title_getter, on_finish_old_track
from src.utils.fsm import MyTracks, MyTracksRejected

my_tracks_menu = Dialog(
    Window(
        Const('Все Ваши работы в одном месте!'),
        # Start(Const('🟢Одобренные🟢'), id='my_tracks_approve'),
        # Start(Const('🟡В процессе🟡'), id='my_tracks_process'),
        Start(Const('🔴Отклоненные🔴'), state=MyTracksRejected.start, id='my_tracks_reject'),
        # Start(Const('Отгруженные'), id='my_tracks_aggregate'),
        Cancel(Const('Назад')),
        state=MyTracks.start
    ),
)

rejected_tracks = Dialog(
    Window(
        Const("Выберите трек"),
        ScrollingGroup(
            Select(
                Format("🔴 {item[0]}"),
                id="ms",
                items="reject_tracks",
                item_id_getter=itemgetter(1),
                on_click=on_item_selected
            ),
            width=1,
            height=5,
            id='scroll_tracks_with_pager',
        ),
        Cancel(),
        getter=tracks_getter,
        state=MyTracksRejected.start,
    ),
    Window(
        Format('*Инфа по треку*'),
        Next(Const('Отправить повторно'), id='rejected_tracks_edit'),
        Cancel(Const('Назад')),
        state=MyTracksRejected.track_info
    ),
    Window(
        Format("Скиньте новый файл трека {title}"),
        Cancel(Const("Назад")),
        MessageInput(set_music_file_for_edit, content_types=[ContentType.AUDIO]),
        MessageInput(other_type_handler_audio),
        state=MyTracksRejected.select_track,
        getter=title_getter
    ),
    Window(
        Const("Подтверждение отправки трека"),
        Row(
            Button(Const("Подтверждаю"), on_click=on_finish_old_track, id="approve_old_track"),
            Back(Const("Изменить"), id="edit_old_track"),
        ),
        Cancel(Const("Вернуться в главное меню")),
        state=MyTracksRejected.finish
    ),
)
