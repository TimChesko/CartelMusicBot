from _operator import itemgetter

from aiogram.types import CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.widgets.kbd import Cancel, ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format

from src.models.tracks import TrackHandler
from src.utils.fsm import AdminListening


async def on_item_selected(callback: CallbackQuery, __, manager: DialogManager, selected_item: str):
    items = eval(selected_item)
    track_id = items[0]
    manager.dialog_data['title'] = items[1]
    # await manager.next()


async def track_list_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    track = await TrackHandler(data['session_maker'], data['database_logger']).get_process_tracks()
    return {
        'tracks': track
    }


tracks = Dialog(
    Window(
        Const('Список треков на прослушивание'),
        ScrollingGroup(
            Select(
                Format("{item[0]}) {item[1]}"),
                id="emp_track_list",
                items="tracks",
                item_id_getter=itemgetter(0, 1),
                on_click=on_item_selected
            ),
            width=1,
            height=5,
            id='scroll_tracks_with_pager',
        ),
        Cancel(),
        state=AdminListening.start,
        getter=track_list_getter
    ),

)
