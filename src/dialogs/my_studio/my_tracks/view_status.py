from operator import itemgetter
from typing import Any

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.api.entities import MediaId, MediaAttachment
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Button, SwitchTo, StubScroll, NumberedPager
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format, Const

from src.dialogs.services.track_info_helper import get_struct_data, get_struct_text, get_attachment_track
from src.dialogs.utils.buttons import TXT_CONFIRM, BTN_BACK, BTN_CANCEL_BACK, TXT_REJECT
from src.dialogs.utils.common import on_start_copy_start_data
from src.models.tables import Track, TrackInfo
from src.models.track_info import TrackInfoHandler
from src.models.tracks import TrackHandler
from src.utils.fsm import ViewStatus, TrackApprove

APPROVE = "approve"
REJECT = "reject"
PROCESS = "process"

STATUS_TEMPLATES = {
    APPROVE: "принят",
    REJECT: "отклонен",
    PROCESS: "в процессе"
}


class DialogManagerOptimized:
    def __init__(self, session_maker, database_logger):
        self.track_handler = TrackHandler(session_maker, database_logger)
        self.track_info_handler = TrackInfoHandler(session_maker, database_logger)

    async def generate_list_buttons(self, dialog_manager: DialogManager) -> dict:
        user_id = dialog_manager.event.from_user.id
        dialog_data = dialog_manager.dialog_data
        tracks = await self.track_handler.get_tracks_and_info_by_status(user_id, dialog_data['status'])

        status = dialog_data['status']
        buttons = []

        for track, track_info in tracks:
            if status == APPROVE and track.status == APPROVE and \
                    (track_info.status is None or track_info.status == APPROVE):
                buttons.append([track.id, track.track_title[:20]])
            elif status in [REJECT, PROCESS] and \
                    (track.status == status or (track_info is not None and track_info.status == status)):
                buttons.append([track.id, track.track_title[:20]])

        return {
            "status": dialog_data['status_text'],
            "status_list": buttons
        }


async def get_buttons(dialog_manager: DialogManager, **_kwargs) -> dict:
    dm_optimized = DialogManagerOptimized(
        dialog_manager.middleware_data['session_maker'],
        dialog_manager.middleware_data['database_logger']
    )
    await dialog_manager.find("stub_scroll_track_info").set_page(0)
    return await dm_optimized.generate_list_buttons(dialog_manager)


async def on_click(callback: CallbackQuery, _, manager: DialogManager, __) -> None:
    manager.dialog_data['track_id'] = int(callback.data.split(":")[-1])
    await manager.switch_to(state=ViewStatus.track)


async def get_data_track(dialog_manager: DialogManager, **_kwargs):
    session_maker = dialog_manager.middleware_data['session_maker']
    database_logger = dialog_manager.middleware_data['database_logger']

    track_handler = TrackHandler(session_maker, database_logger)
    track_info_handler = TrackInfoHandler(session_maker, database_logger)

    track_id = int(dialog_manager.dialog_data['track_id'])
    track = await track_handler.get_track_by_id(track_id)
    track_info = await track_info_handler.get_docs_by_id(track_id)

    text, files = await create_text_and_files(track, track_info)
    file_type, file_id = await get_attachment_track(dialog_manager, files, track, "stub_scroll_track_info")

    return {
        "pages": len(files.keys()) if files else 0,
        "text": text,
        "attachment": MediaAttachment(file_type, file_id=MediaId(file_id)),
        "new_data": track.status == APPROVE and track_info.status is None,
        "edit_data": track.status == APPROVE and track_info.status == REJECT,
        "delete": track.status in [PROCESS, REJECT]
    }


async def create_text_and_files(track: Track, track_info: TrackInfo) -> tuple[str, dict | None]:
    text = f"Трек: {track.track_title}\n\n"
    files = None
    status_track = STATUS_TEMPLATES[track.status]
    text += f"Статус трека: <b>{status_track}</b>\n"
    if track_info.status:
        if track_info.status != PROCESS:
            status_info = STATUS_TEMPLATES[track_info.status]
            text += f"Статус информации по треку: <b>{status_info}</b>\n"
        if track_info.status == APPROVE:
            files, track_info_text = await get_struct_data(track_info)
            text += await get_struct_text(track_info_text)
    return text, files


async def delete_track(_, __, dialog_manager: DialogManager):
    session_maker = dialog_manager.middleware_data['session_maker']
    database_logger = dialog_manager.middleware_data['database_logger']
    track_id = dialog_manager.dialog_data['track_id']
    await TrackHandler(session_maker, database_logger).delete_track_by_id(int(track_id))
    await dialog_manager.switch_to(ViewStatus.menu)


async def start_form(_, __, manager: DialogManager):
    data = {'track_id': manager.dialog_data['track_id'], }
    await manager.start(state=TrackApprove.title, data=data)


async def on_process(_, result: Any, manager: DialogManager):
    session_maker = manager.middleware_data['session_maker']
    database_logger = manager.middleware_data['database_logger']
    track_handler = TrackHandler(session_maker, database_logger)

    track_id = int(manager.dialog_data['track_id'])
    user_id = manager.event.from_user.id
    status = manager.dialog_data['status']

    if result is not None and result[0]:
        await track_handler.delete_track_by_id(track_id)
    elif not await track_handler.get_tracks_by_status(user_id, status):
        return await manager.done()

    return await manager.switch_to(ViewStatus.menu)


dialog = Dialog(
    Window(
        Const("Список треков:"),
        Format("<b>{status}</b>"),
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
        BTN_CANCEL_BACK,
        state=ViewStatus.menu,
        getter=get_buttons,
    ),
    Window(
        Format("{text}"),
        DynamicMedia('attachment'),
        StubScroll(id="stub_scroll_track_info", pages="pages"),
        NumberedPager(
            scroll="stub_scroll_track_info"
        ),
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
        BTN_BACK,
        getter=get_data_track,
        state=ViewStatus.track
    ),
    Window(
        Const("Подтвердите действие"),
        SwitchTo(TXT_REJECT, id="my_studio_cancel", state=ViewStatus.menu),
        Button(TXT_CONFIRM, id="my_studio_accept", on_click=delete_track),
        state=ViewStatus.accept
    ),
    on_process_result=on_process,
    on_start=on_start_copy_start_data
)
