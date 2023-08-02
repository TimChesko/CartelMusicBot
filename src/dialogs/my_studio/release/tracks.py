import logging
from _operator import itemgetter

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Button, Start, Next, Cancel, SwitchTo, Multiselect
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format

from src.models.album import AlbumHandler
from src.models.tables import Album
from src.models.track import TrackHandler
from src.utils.fsm import ReleaseTrack, AlbumTitle, AlbumPage, AlbumCover, AlbumTracks


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
    logging.info(dialog_manager.start_data['album_id'])
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
            width=1,
            height=4
        ),
        Button(Const('Готово'), on_click=on_track_select, id='finish_select'),
        Cancel(Const('Назад')),
        state=AlbumTracks.start,
        getter=tracks_getter
    )
)
