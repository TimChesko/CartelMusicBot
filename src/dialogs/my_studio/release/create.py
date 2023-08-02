import logging
from _operator import itemgetter

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Button, Cancel
from aiogram_dialog.widgets.text import Const, Format

from src.models.album import AlbumHandler
from src.utils.fsm import ReleaseTrack, AlbumPage


async def on_album_selected(callback: CallbackQuery, __, manager: DialogManager, selected_item: str):
    items = eval(selected_item)
    logging.info(type(items[0]))
    await manager.start(AlbumPage.main, data={'album_id': items[0],
                                              'title': items[1]}, show_mode=ShowMode.EDIT)


async def list_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    logging.info(dialog_manager.event.from_user.id)
    album = await AlbumHandler(data['session_maker'], data['database_logger']).get_album_by_user_id(
        dialog_manager.event.from_user.id)
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
                Format("{item[1]}"),
                id="ms",
                items="albums",
                item_id_getter=itemgetter(0, 1),
                on_click=on_album_selected
            ),
            width=1,
            height=5,
            id='scroll_tracks_with_pager',
        ),
        Button(Const('Создать'), on_click=create_album, id='create_new_album'),
        Cancel(),
        getter=list_getter,
        state=ReleaseTrack.list
    )
)
