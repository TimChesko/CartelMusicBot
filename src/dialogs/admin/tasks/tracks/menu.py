from operator import itemgetter

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.utils.buttons import BTN_CANCEL_BACK
from src.models.track_info import TrackInfoHandler
from src.utils.enums import Status
from src.utils.fsm import AdminCheckTrack, AdminListTracks


async def formatting_docs(docs: list) -> list:
    new_docs = []
    for item in docs:
        new_docs.append([item.track_id, item.title[:20]])
    return new_docs


async def get_data(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    docs = await TrackInfoHandler(data['session_maker'], data['database_logger']).get_docs_by_status(Status.PROCESS)
    return {
        "tasks": await formatting_docs(docs)
    }


async def on_item_selected(_, __, manager: DialogManager, selected_item: str):
    await manager.start(state=AdminCheckTrack.menu, data={"track_id": int(selected_item)})


dialog = Dialog(
    Window(
        Const("Список треков на проверку"),
        ScrollingGroup(
            Select(
                Format("{item[1]}"),
                id="emp_track_list",
                items="tasks",
                item_id_getter=itemgetter(0),
                on_click=on_item_selected
            ),
            width=1,
            height=5,
            id='scroll_tracks_with_pager',
            hide_on_single_page=True
        ),
        BTN_CANCEL_BACK,
        getter=get_data,
        state=AdminListTracks.menu
    )
)
