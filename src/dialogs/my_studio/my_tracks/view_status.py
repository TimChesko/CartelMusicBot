from operator import itemgetter

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.api.entities import MediaId, MediaAttachment
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Cancel, Button, Back
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format, Const

from src.dialogs.utils.common import on_start_copy_start_data
from src.models.tracks import TrackHandler
from src.utils.fsm import ViewStatus


async def get_data_list(dialog_manager: DialogManager, **_kwargs) -> dict:
    middleware_data = dialog_manager.middleware_data
    user_id = middleware_data['event_from_user'].id
    dialog_data = dialog_manager.dialog_data
    tracks = await TrackHandler(middleware_data['session_maker'], middleware_data['database_logger']). \
        get_tracks_by_status(user_id, dialog_data['status'])
    buttons = [[track.id, track.track_title] for track in tracks]
    return {
        "status": dialog_data['status'],
        "status_list": buttons
    }


async def on_click(callback: CallbackQuery, _, manager: DialogManager, __) -> None:
    manager.dialog_data['track_id'] = callback.data.split(":")[-1]
    await manager.switch_to(state=ViewStatus.track)


async def create_text(track) -> str:
    return track.track_title


async def get_data_track(dialog_manager: DialogManager, **_kwargs):
    middleware_data = dialog_manager.middleware_data
    dialog_data = dialog_manager.dialog_data
    track = await TrackHandler(middleware_data['session_maker'], middleware_data['database_logger']). \
        get_track_by_id(int(dialog_data['track_id']))
    text = await create_text(track)
    return {
        "text": text,
        "audio": MediaAttachment(ContentType.AUDIO, file_id=MediaId(track.file_id_audio))
    }


async def delete_track():
    pass


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
            Const("Удалить трек"),
            id="my_studio_status_process_delete",
            on_click=delete_track,
            when=...
        ),
        Button(
            Const("Заполнить данные"),
            id="my_studio_status_approve_write",
            on_click=...,
            when=...
        ),
        Button(
            Const("Заполнить данные"),
            id="my_studio_status_approve",
            on_click=...,
            when=...
        ),
        Button(
            Const("Отправить новый трек"),
            id="my_studio_status_approve",
            on_click=...,
            when=...
        ),
        Back(Const("< Назад")),
        getter=get_data_track,
        state=ViewStatus.track
    ),
    on_start=on_start_copy_start_data
)
