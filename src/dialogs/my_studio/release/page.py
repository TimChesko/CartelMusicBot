import logging

from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.utils.buttons import BTN_CANCEL_BACK
from src.models.album import AlbumHandler
from src.utils.fsm import AlbumPage, AlbumTracks


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
    album, tracks = await AlbumHandler(data['session_maker'], data['database_logger']).get_album_scalar(
        dialog_manager.start_data['album_id'])
    is_cover = None
    if album.album_cover:
        is_cover = MediaAttachment(ContentType.DOCUMENT, file_id=MediaId(album.album_cover))
    return {
        'data': dialog_manager.start_data,
        'title': dialog_manager.start_data['title'],
        'cover': is_cover,
        'tracks': '\n'.join(tracks) if tracks is not None else "",
        'text_title': '✓ Название' if album.album_title else 'Дать название',
        'text_cover': '✓ Обложка' if album.album_cover else 'Прикрепить обложку',
        'text_tracks': '✓ Треки' if tracks is not None else 'Прикрепить треки'
    }


async def choose_track(__, _, manager: DialogManager):
    await manager.start(state=AlbumTracks.start, data={'album_id': manager.start_data['album_id']},
                        show_mode=ShowMode.EDIT)


async def clear_tracks(__, _, manager: DialogManager):
    data = manager.middleware_data
    await AlbumHandler(data['session_maker'], data['database_logger']).delete_album_id_from_tracks(
        manager.start_data['album_id'])


async def delete_release(__, _, manager: DialogManager):
    data = manager.middleware_data
    await AlbumHandler(data['session_maker'], data['database_logger']).delete_release(manager.start_data['album_id'])
    await manager.done()


main = Dialog(
    Window(
        Format("Релиз: '{title}' "),
        Format("Треки в этом релизе: \n{tracks}"),
        DynamicMedia('cover'),
        SwitchTo(Format('{text_title}'), id='create_album_title', state=AlbumPage.title),
        SwitchTo(Format('{text_cover}'), id='create_album_cover', state=AlbumPage.cover),
        Button(Format('{text_tracks}'), id='add_tracks_to_album', on_click=choose_track),
        Button(Const('Очистить треки'), on_click=clear_tracks, id='clear_tracks'),
        Button(Const('Удалить'), on_click=delete_release, id='delete_release'),
        BTN_CANCEL_BACK,
        state=AlbumPage.main,
        getter=getter
    ),
    title,
    cover
)
