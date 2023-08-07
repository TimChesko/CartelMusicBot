import logging
from operator import itemgetter
from typing import Any

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.api.entities import MediaId, MediaAttachment
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Cancel, Button, Back, SwitchTo
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format, Const

from src.dialogs.utils.buttons import TXT_CONFIRM
from src.dialogs.utils.common import on_start_copy_start_data
from src.models.track_info import TrackInfoHandler
from src.models.tracks import TrackHandler
from src.utils.fsm import ViewStatus, TrackApprove


# LIST MENU

async def get_data_list(dialog_manager: DialogManager, **_kwargs) -> dict:
    middleware_data = dialog_manager.middleware_data
    user_id = middleware_data['event_from_user'].id
    dialog_data = dialog_manager.dialog_data
    tracks = await TrackHandler(middleware_data['session_maker'], middleware_data['database_logger']). \
        get_tracks_and_info_by_status(user_id, dialog_data['status'])
    logging.debug(tracks)
    buttons = []
    status = dialog_data['status']
    logging.debug(status)
    for track, track_info in tracks:
        logging.debug(track)
        if status == "approve" and track.status == status and \
                (track_info.status is None or track_info.status == status):
            buttons.append([track.id, track.track_title[:20]])
        elif status in ["reject", "process"] and \
                (track.status == status or (track_info is not None and track_info.status == status)):
            buttons.append([track.id, track.track_title[:20]])
    return {
        "status": status,
        "status_list": buttons
    }


async def on_click(callback: CallbackQuery, _, manager: DialogManager, __) -> None:
    manager.dialog_data['track_id'] = callback.data.split(":")[-1]
    await manager.switch_to(state=ViewStatus.track)


# TRACK INFO


async def get_data_track(dialog_manager: DialogManager, **_kwargs):
    middleware_data = dialog_manager.middleware_data
    dialog_data = dialog_manager.dialog_data
    track = await TrackHandler(middleware_data['session_maker'], middleware_data['database_logger']). \
        get_track_by_id(int(dialog_data['track_id']))
    track_info = await TrackInfoHandler(middleware_data['session_maker'], middleware_data['database_logger']). \
        get_docs_by_id(int(dialog_data['track_id']))
    new_data = track.status == "approve" and track_info.status is None
    edit_data = track.status == "approve" and track_info.status == "reject"
    text = await create_text(track, track_info)
    return {
        "text": text,
        "audio": MediaAttachment(ContentType.AUDIO, file_id=MediaId(track.file_id_audio)),
        "new_data": new_data,
        "edit_data": edit_data,
        "delete": True if track.status == "process" or track.status == "reject" else False
    }


async def create_text(track, track_info) -> str:
    text = f"Трек: {track.track_title}\n\n"
    template_status = {
        "approve": "принят",
        "reject": "отклонен",
        "process": "в процессе"
    }
    status_track = template_status[track.status]
    text += f"Статус трека: {status_track}\n"
    if track_info.status and track.status != "process":
        status_info = template_status[track_info.status]
        text += f"Статус информации по треку: {status_info}"
    return text


async def delete_track(_, __, manager: DialogManager):
    middleware_data = manager.middleware_data
    track_id = manager.dialog_data['track_id']
    await TrackHandler(middleware_data['session_maker'], middleware_data['database_logger']). \
        delete_track_by_id(int(track_id))
    await manager.switch_to(ViewStatus.menu)


async def start_form(_, __, manager: DialogManager):
    data = {'track_id': manager.dialog_data['track_id'], }
    await manager.start(state=TrackApprove.title, data=data)


# UTILS

async def on_process(_, result: Any, manager: DialogManager):
    middleware_data = manager.middleware_data
    dialog_data = manager.dialog_data
    user_id = middleware_data['event_from_user'].id
    track_handler = TrackHandler(middleware_data['session_maker'], middleware_data['database_logger'])
    if result is not None and result[0] is True:
        await track_handler.delete_track_by_id(int(manager.dialog_data['track_id']))
    elif len(await track_handler.get_tracks_by_status(user_id, dialog_data['status'])) == 0:
        return await manager.done()
    return await manager.switch_to(ViewStatus.menu)


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
        Cancel(Const("< Назад")),
        state=ViewStatus.menu,
        getter=get_data_list,
    ),
    Window(
        Format("{text}"),
        DynamicMedia('audio'),
        Button(
            Const("Заполнить данные"),
            id="my_studio_status_approve",
            on_click=start_form,
            when="new_data"
        ),
        Button(
            Const("Заполнить заново данные"),
            id="my_studio_status_reject",
            on_click=start_form,
            when="edit_data"
        ),
        SwitchTo(
            Const("Удалить трек"),
            id="my_studio_status_process_delete",
            state=ViewStatus.accept,
            when="delete"
        ),
        Back(Const("< Назад")),
        getter=get_data_track,
        state=ViewStatus.track
    ),
    Window(
        Const("Подтвердите действие"),
        Button(TXT_CONFIRM, id="my_studio_accept", on_click=delete_track),
        SwitchTo(Const("Отменить"), id="my_studio_cancel", state=ViewStatus.menu),
        state=ViewStatus.accept
    ),
    on_process_result=on_process,
    on_start=on_start_copy_start_data
)
