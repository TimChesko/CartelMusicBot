from _operator import itemgetter

from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Cancel, Button, Back, Row, Next
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.listening.edit import on_item_selected, set_music_file_for_edit, on_finish_old_track, \
    on_finish_getter
from src.dialogs.listening.menu import tracks_getter
from src.dialogs.listening.new import other_type_handler_audio
from src.utils.fsm import MyTracksRejected

reloading_on_listening = Dialog(
    Window(
        Const("Выберите трек"),
        ScrollingGroup(
            Select(
                Format("🔴 {item[0]}"),
                id="rejected_tracks_item",
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
        getter=on_finish_getter
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
