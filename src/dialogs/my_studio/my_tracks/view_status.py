import logging
from operator import itemgetter

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Back
from aiogram_dialog.widgets.text import Format, Const

from src.models.tracks import TrackHandler
from src.utils.fsm import ViewStatus


async def on_click(callback: CallbackQuery, _, manager: DialogManager, __):
    pass


async def get_data(dialog_manager: DialogManager, **_kwargs):
    middleware_data = dialog_manager.middleware_data
    user_id = middleware_data['event_from_user'].id
    dialog_data = dialog_manager.dialog_data
    tracks = await TrackHandler(middleware_data['session_maker'], middleware_data['database_logger']).\
        get_tracks_by_status(user_id, dialog_data['status'])
    logging.info(tracks)
    return {}


async def on_start(_, dialog_manager: DialogManager):
    dialog_manager.dialog_data['status'] = dialog_manager.start_data['status']
    del dialog_manager.start_data['status']


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
        Back(Const("Назад")),
        getter=get_data,
        state=ViewStatus.menu
    ),
    on_start=on_start
)
