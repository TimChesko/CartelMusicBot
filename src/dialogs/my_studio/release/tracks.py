import logging
from _operator import itemgetter

from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import ScrollingGroup, Button, Multiselect
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.utils.buttons import BTN_CANCEL_BACK
from src.models.track import TrackHandler
from src.utils.fsm import AlbumTracks


async def on_track_select(__, _, manager: DialogManager):
    data = manager.middleware_data
    widget = manager.find('album_tracklist')
    tracklist = widget.get_checked()
    logging.info(manager.start_data['album_id'])
    await TrackHandler(data['session_maker'], data['database_logger']).update_album_id(list(map(int, tracklist)),
                                                                                       manager.start_data['album_id'])
    await manager.done()


async def tracks_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    tracks = await TrackHandler(data['session_maker'], data['database_logger']).get_for_album_multiselect(
        dialog_manager.event.from_user.id)
    return {
        'items': tracks
    }


choose_track = Dialog(
    Window(
        Const('Выберите треки, которые нужно добавить в альбом'),
        ScrollingGroup(
            Multiselect(
                Format('✓ {item[0]}'),
                Format('{item[0]}'),
                id='album_tracklist',
                items='items',
                item_id_getter=itemgetter(1),
            ),
            id='scroll_album',
            hide_on_single_page=True,
            # hide_pager=True,
            width=1,
            height=4
        ),
        Button(Const('Готово'), on_click=on_track_select, id='finish_select'),
        BTN_CANCEL_BACK,
        state=AlbumTracks.start,
        getter=tracks_getter
    )
)
