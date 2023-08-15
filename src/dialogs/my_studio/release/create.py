from _operator import itemgetter

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Button
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.utils.buttons import BTN_CANCEL_BACK
from src.models.release import ReleaseHandler
from src.utils.fsm import ReleaseTrack, ReleasePage


async def on_release_selected(_, __, manager: DialogManager, selected_item: str):
    release_id = int(selected_item)
    await manager.start(ReleasePage.main, data={'release_id': release_id}, show_mode=ShowMode.EDIT)


async def list_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    release = await ReleaseHandler(data['session_maker'], data['database_logger']).get_release_by_user_id(
        dialog_manager.event.from_user.id)
    return {
        'releases': [(release_id, title if title else 'Новый альбом') for release_id, title in release]
    }


async def create_release(callback: CallbackQuery, __, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).add_new_release(callback.from_user.id)


main = Dialog(
    Window(
        Const("Создайте или выберите работу"),
        ScrollingGroup(
            Select(
                Format("🎵 {item[1]}"),
                id="ms",
                items="releases",
                item_id_getter=itemgetter(0),
                on_click=on_release_selected
            ),
            width=1,
            height=5,
            id='scroll_tracks_with_pager',
            hide_on_single_page=True
        ),
        Button(Const('❇️ Создать'), on_click=create_release, id='create_new_release'),
        BTN_CANCEL_BACK,
        getter=list_getter,
        state=ReleaseTrack.list
    )
)
