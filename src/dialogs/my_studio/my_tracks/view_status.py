from operator import itemgetter

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Format

from src.utils.fsm import ViewStatus


async def on_click(callback: CallbackQuery, _, manager: DialogManager, __):
    pass


async def get_data(dialog_manager: DialogManager, **_kwargs):
    return {}


dialog = Dialog(
    Window(
        Format("Список треков: {status}"),
        ScrollingGroup(
            Select(
                Format("{item[1]}"),
                id="scroll_status",
                items="status_list",
                item_id_getter=itemgetter(0),
                on_click=on_click
            ),
            width=1,
            height=5,
            hide_on_single_page=True,
            id='scroll_my_studio_status',
        ),
        getter=get_data,
        state=ViewStatus.menu
    )
)
