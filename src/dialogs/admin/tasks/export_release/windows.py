from _operator import itemgetter

from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Row, Button, StubScroll, NumberedPager
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.admin.tasks.export_release import getters, handlers
from src.dialogs.utils.buttons import BTN_CANCEL_BACK, BTN_BACK
from src.utils.fsm import AdminExportRelease

export_release = Dialog(

    #  Список релизов
    Window(
        Const('Список релизов на выгрузку'),
        ScrollingGroup(
            Select(
                Format("Релиз №{item[0]}"),
                id="release",
                items="list_release",
                item_id_getter=itemgetter(0),
                on_click=handlers.on_release
            ),
            width=1,
            height=5,
            id='scroll_release_with_pager',
            hide_on_single_page=True
        ),
        BTN_CANCEL_BACK,
        state=AdminExportRelease.start,
        getter=getters.release_list_getter
    ),

    #  Информация по релизу (текст) и список треков (кнопки)
    Window(
        Format("Выбранный файл: {pick_file}"),
        Format("Название релиза: {release_title}"),
        DynamicMedia("attachment"),
        StubScroll(id="release_stub_scroll", pages="release_pages"),
        NumberedPager(
            scroll="release_stub_scroll",
        ),
        ScrollingGroup(
            Select(
                Format("{item[1]}"),
                id="release_tracks",
                items="list_tracks",
                item_id_getter=itemgetter(0),
                on_click=handlers.on_track
            ),
            width=1,
            height=5,
            id='scroll_release_tracks_with_pager',
            hide_on_single_page=True
        ),
        BTN_BACK,
        state=AdminExportRelease.view_release,
        getter=getters.tracks_list_getter
    ),

    #  Информация по треку (текст)
    Window(
        Format("{text}"),

        state=AdminExportRelease.view_track,
        getter=getters.track_getter
    )
)
