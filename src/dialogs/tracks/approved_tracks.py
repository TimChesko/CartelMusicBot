import logging
from _operator import itemgetter
from typing import Any

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Cancel, Button, Back, Row, Next
from aiogram_dialog.widgets.text import Const, Format

from src.models.tracks import TrackHandler
from src.utils.fsm import MyTracksApproved


async def tracks_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    approved = await TrackHandler(data['engine'], data['database_logger']).get_approved_by_tg_id(
        data['event_from_user'].id)
    return {
        'approved_tracks': approved
    }


async def on_item_selected(
        callback: CallbackQuery,
        widget: Any,
        manager: DialogManager,
        selected_item: str):
    manager.dialog_data["track_id"] = int(selected_item)
    logging.info(selected_item)
    await manager.next()


approved_filling_data = Dialog(
    Window(
        Const("Выберите трек"),
        ScrollingGroup(
            Select(
                Format("🟢 {item[0]}"),
                id="approved_tracks_item",
                items="approved_tracks",
                item_id_getter=itemgetter(1),
                on_click=on_item_selected
            ),
            width=1,
            height=5,
            id='scroll_tracks_with_pager',
        ),
        Cancel(),
        getter=tracks_getter,
        state=MyTracksApproved.start,
    )
)
