import logging

from aiogram.enums import ContentType
from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Back, Cancel, Checkbox
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format, List

from src.dialogs.utils.buttons import BTN_CANCEL_BACK, TXT_CONFIRM, TXT_REJECT, BTN_BACK, TXT_BACK
from src.models.album import AlbumHandler
from src.utils.fsm import AdminReleaseLvl1


async def task_page_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    user, track, album = await AlbumHandler(data['session_maker'],
                                            data['database_logger']).get_tracks_and_personal_data(
        dialog_manager.dialog_data['user_id'],
        dialog_manager.dialog_data['album_id'])
    doc_id = album.unsigned_license if dialog_manager.dialog_data['doc_state'] is True else album.album_cover
    doc = MediaAttachment(ContentType.DOCUMENT, file_id=MediaId(doc_id))
    return {
        'username': user.tg_username if user.tg_username else user.tg_id,
        'nickname': user.nickname,
        'title': album.album_title,
        'tracks': track,
        'doc': doc
    }


async def cancel_task(_, __, manager: DialogManager):
    data = manager.middleware_data
    await AlbumHandler(data['session_maker'], data['database_logger']).set_task_state(manager.dialog_data['album_id'],
                                                                                      None)
    manager.show_mode = ShowMode.EDIT


async def change_state(_, __, manager: DialogManager):
    state = manager.dialog_data['doc_state']
    if state is True:
        manager.dialog_data['doc_state'] = False
    else:
        manager.dialog_data['doc_state'] = True

task_page = Window(
    DynamicMedia('doc'),
    Format('Название релиза:{title}'),
    Format('Артист: {username} / {nickname}'),
    List(Format('{item.id})  "{item.track_title}"'), items='tracks'),
    Checkbox(Const("🔘 Договор/Обложка"),
             Const("Договор/Обложка 🔘"),
             id='swap_docs',
             on_click=change_state,
             default=True),
    Back(Const(TXT_CONFIRM), id='approve_album', on_click=...),
    Back(Const(TXT_REJECT), id='reject_album', on_click=...),
    Cancel(Const(TXT_BACK), on_click=cancel_task),
    state=AdminReleaseLvl1.info,
    getter=task_page_getter
)


async def on_track_selected(callback: CallbackQuery, __, manager: DialogManager, selected_item):
    item = int(selected_item)
    data = manager.middleware_data
    album = await AlbumHandler(data['session_maker'], data['database_logger']).get_album_first(item)
    if album.checker is None or album.checker == callback.from_user.id:
        await AlbumHandler(data['session_maker'], data['database_logger']).set_task_state(item,
                                                                                          callback.from_user.id)
        manager.dialog_data['album_id'] = item
        manager.dialog_data['user_id'] = album.user_id
        manager.dialog_data['doc_state'] = True
        await manager.next()
    else:
        await callback.answer('Этот трек уже в работе!')
        await manager.switch_to(AdminReleaseLvl1.start)


async def lvl1_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    album = await AlbumHandler(data['session_maker'], data['database_logger']).get_unsigned_state('process')
    logging.info(album)
    return {
        'album': album
    }


choose = Dialog(
    Window(
        Const('Список тасков 1 уровень: \n'
              'Обложка + название + список треков + первичное ЛД'),
        ScrollingGroup(
            Select(
                Format("{item.id}) {item.album_title}"),
                id="alb_adm_track_list",
                items="album",
                item_id_getter=lambda album: album.id,
                on_click=on_track_selected
            ),
            width=1,
            height=5,
            id='scroll_albums_lvl1',
            hide_on_single_page=True
        ),
        BTN_CANCEL_BACK,
        state=AdminReleaseLvl1.start,
        getter=lvl1_getter
    ),
    task_page,
)
