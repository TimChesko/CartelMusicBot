from _operator import itemgetter

from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.utils.buttons import BTN_CANCEL_BACK
from src.utils.fsm import AdminExportRelease
from src.dialogs.admin.tasks.export_release import getters, handlers

export_release = Dialog(
    Window(
        Const('Список релизов на выгрузку'),
        ScrollingGroup(
            Select(
                Format("Релиз №{item[0]}"),
                id="release",
                items="list_release",
                item_id_getter=itemgetter(0),
                on_click=handlers.on_item
            ),
            width=1,
            height=5,
            id='scroll_release_with_pager',
            hide_on_single_page=True
        ),
        BTN_CANCEL_BACK,
        state=AdminExportRelease.start,
        getter=getters.release_list_getter
    )
)
