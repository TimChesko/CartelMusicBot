from _operator import itemgetter

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.utils.buttons import BTN_CANCEL_BACK
from src.utils.fsm import AdminReleaseLvl1


async def lvl1_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data



    return {

    }


choose = Dialog(
    Window(
        Const('Список тасков 1 уровень: \n'
              'Обложка + название + список треков + первичное ЛД'),
        ScrollingGroup(
            Select(
                Format("{item[0]}) {item[1]}"),
                id="emp_track_list",
                items="tracks",
                item_id_getter=itemgetter(0, 1),
                on_click=...
            ),
            width=1,
            height=5,
            id='scroll_albums_lvl1',
            hide_on_single_page=True
        ),
        BTN_CANCEL_BACK,
        state=AdminReleaseLvl1.start,
        getter=lvl1_getter
    )
)
