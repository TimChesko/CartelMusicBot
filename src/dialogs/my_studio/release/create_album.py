import logging
from _operator import itemgetter

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Button
from aiogram_dialog.widgets.text import Const, Format

from src.models.track_info import AlbumHandler
from src.utils.fsm import ReleaseTrack


async def list_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    logging.info(dialog_manager.event.from_user.id)
    logging.info(await AlbumHandler(data['session_maker'], data['database_logger']).get_album_by_user_id(
        dialog_manager.event.from_user.id))
    album = await AlbumHandler(data['session_maker'], data['database_logger']).get_album_by_user_id(
        dialog_manager.event.from_user.id)
    logging.info([(album_id, title if title else 'Новый альбом') for album_id, title in album])
    return {
        'albums': [(album_id, title if title else 'Новый альбом') for album_id, title in album]
    }


async def create_album(callback: CallbackQuery, __, manager: DialogManager):
    data = manager.middleware_data
    await AlbumHandler(data['session_maker'], data['database_logger']).add_new_album(callback.from_user.id)


main = Dialog(
    Window(
        Const("Создайте или выберите работу"),
        ScrollingGroup(
            Select(
                Format("{item[0]}# {item[1]}"),
                id="ms",
                items="albums",
                item_id_getter=itemgetter(0),
                on_click=...
            ),
            width=1,
            height=5,
            id='scroll_tracks_with_pager',
        ),
        Button(Const('Создать'), on_click=create_album, id='create_new_album'),
        getter=list_getter,
        state=ReleaseTrack.list
    )
)
