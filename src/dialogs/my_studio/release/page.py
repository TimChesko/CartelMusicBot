import logging
from _operator import itemgetter

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Button, Start, Next, Cancel, SwitchTo
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format

from src.models.album import AlbumHandler
from src.models.tables import Album
from src.utils.fsm import ReleaseTrack, AlbumTitle, AlbumPage, AlbumCover, AlbumTracks


async def set_album_cover(msg: Message, _, manager: DialogManager):
    data = manager.middleware_data
    logging.info(msg.document.file_id)
    await AlbumHandler(data['session_maker'], data['database_logger']).set_cover(manager.start_data['album_id'],
                                                                                 msg.document.file_id)
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    await manager.switch_to(AlbumPage.main)


async def other_type_handler_doc(msg: Message, _, __):
    await msg.delete()
    await msg.answer("Пришлите обложку альбома в виде файла")


cover = Window(
    Const("Прикрепите новую обложку в виде фото без сжатия"),
    MessageInput(set_album_cover, content_types=[ContentType.DOCUMENT]),
    MessageInput(other_type_handler_doc),
    state=AlbumPage.cover
)


async def set_album_title(msg: Message, _, manager: DialogManager):
    data = manager.middleware_data
    await AlbumHandler(data['session_maker'], data['database_logger']).set_title(manager.start_data['album_id'],
                                                                                 msg.text)
    manager.start_data['title'] = msg.text
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    await manager.back()


async def other_type_handler_text(msg: Message, _, __):
    await msg.delete()
    await msg.answer("Пришлите название альбома в виде сообщения")


title = Window(
    Const("Дайте название альбому"),
    MessageInput(set_album_title, content_types=[ContentType.TEXT]),
    MessageInput(other_type_handler_text),
    state=AlbumPage.title
)


async def getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    album = await AlbumHandler(data['session_maker'], data['database_logger']).get_album_scalar(
        dialog_manager.start_data['album_id'])
    if album.album_cover:
        cover = MediaAttachment(ContentType.DOCUMENT, file_id=MediaId(album.album_cover))
    return {
        'data': dialog_manager.start_data,
        'title': dialog_manager.start_data['title'],
        'cover': cover if album.album_cover else None,
    }


async def choose_track(__, _, manager: DialogManager):
    await manager.start(state=AlbumTracks.start, data={'album_id': manager.start_data['album_id']},
                        show_mode=ShowMode.EDIT)


main = Dialog(
    Window(
        Format("Релиз: {title}\n "),
        DynamicMedia('cover'),
        # TODO переделать константы в формат, идея с галочкой, когда есть запись в бд
        SwitchTo(Const('Название альбома'), id='create_album_title', state=AlbumPage.title),
        SwitchTo(Const('Обложка альбома'), id='create_album_cover', state=AlbumPage.cover),
        Button(Const('Выбор треков'), id='add_tracks_to_album', on_click=choose_track),
        Cancel(Const('Назад'), id='cancel_albums1'),
        state=AlbumPage.main,
        getter=getter
    ),
    title,
    cover
)
