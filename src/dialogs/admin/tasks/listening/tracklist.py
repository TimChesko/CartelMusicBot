from _operator import itemgetter

from aiogram.types import CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.admin.tasks.listening.custom import reason_window, confirm_reason_window
from src.dialogs.admin.tasks.listening.on_track import info_window, reject_templates
from src.dialogs.utils.buttons import BTN_CANCEL_BACK
from src.models.tracks import TrackHandler
from src.utils.fsm import AdminListening


async def on_item_selected(callback: CallbackQuery, __, manager: DialogManager, selected_item: str):
    items = eval(selected_item)
    data = manager.middleware_data
    local = manager.dialog_data
    track_id = items[0]
    checker, file, title, user = await TrackHandler(data['session_maker'], data['database_logger']).get_listening_info(
        track_id)
    if checker is None or checker == callback.from_user.id:
        await TrackHandler(data['session_maker'], data['database_logger']).set_task_state(track_id,
                                                                                          callback.from_user.id)
        local['file'] = file
        local['getter_info'] = {
            'track_id': track_id,
            'title': title,
            'user_id': user.tg_id,
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


tracks = Dialog(
    Window(
        Const('Список треков на прослушивание'),
        ScrollingGroup(
            Select(
                Format("Прослушивание №{item[0]}"),
                id="emp_track_list",
                items="tracks",
                item_id_getter=itemgetter(0),
                on_click=on_item_selected
            ),
            width=1,
            height=5,
            id='scroll_tracks_with_pager',
            hide_on_single_page=True
        ),
        BTN_CANCEL_BACK,
        state=AdminListening.start,
        getter=track_list_getter
    ),
    info_window,
    reject_templates,
    reason_window,
    confirm_reason_window
)
