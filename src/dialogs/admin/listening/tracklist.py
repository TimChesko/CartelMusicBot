import logging
from _operator import itemgetter

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import Start, Cancel, ScrollingGroup, Select, Group, SwitchTo, Back
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format

from src.data import config
from src.dialogs.admin.dashboard.employee.delete import delete_window
from src.dialogs.admin.dashboard.employee.info import info_window
from src.dialogs.admin.dashboard.employee.privilege import privilege_window
from src.models.employee import EmployeeHandler
from src.models.tables import Track
from src.models.tracks import TrackHandler
from src.utils.fsm import AdminEmployee, AdminAddEmployee, AdminListening


async def on_item_selected(callback: CallbackQuery, __, manager: DialogManager, selected_item: str):
    items = eval(selected_item)
    data = manager.middleware_data
    local = manager.dialog_data
    track_id = items[0]
    checker, file, user = await TrackHandler(data['session_maker'], data['database_logger']).get_listening_info(
        track_id)
    if checker is None or checker == callback.from_user.id:
        await TrackHandler(data['session_maker'], data['database_logger']).update_checker(track_id,
                                                                                          data['event_from_user'].id)
        local['file'] = file
        local['getter_info'] = {
            'track_id': track_id,
            'title': items[1],
            'nickname': user.nickname,
            'username': '@' + user.tg_username if user.tg_username is not None else user.tg_id
        }
        await manager.next()
    else:
        await callback.answer('Этот трек уже в работе!')
        await manager.switch_to(AdminListening.start)


async def track_list_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    track = await TrackHandler(data['session_maker'], data['database_logger']).get_process_tracks()
    return {
        'tracks': track
    }


async def info_getter(dialog_manager: DialogManager, **_kwargs):
    audio = MediaAttachment(ContentType.AUDIO, file_id=MediaId(dialog_manager.dialog_data['file']))
    return {
        **dialog_manager.dialog_data['getter_info'],
        'audio': audio
    }


async def cancel_task(callback: CallbackQuery, _, manager: DialogManager):
    data = manager.middleware_data
    track_id = manager.dialog_data['getter_info']['track_id']
    await TrackHandler(data['session_maker'], data['database_logger']).update_checker(track_id, None)


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
    Window(
        Format('Уникальный номер: {track_id}'),
        Format('Название: {title}'),
        Format('Артист: {nickname} | {username}'),
        DynamicMedia('audio'),
        Back(Const('Назад'), on_click=cancel_task),
        state=AdminListening.info,
        getter=info_getter
    )
)
