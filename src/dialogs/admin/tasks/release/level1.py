import logging

from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Back, Cancel, Checkbox, SwitchTo, Button
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format, List

from src.dialogs.admin.tasks.release.funcs import confirm_release, reject_release, on_task_selected, cancel_task, \
    create_reason_window, create_reason_confirm_window
from src.dialogs.utils.buttons import BTN_CANCEL_BACK, TXT_CONFIRM, TXT_BACK, coming_soon
from src.models.album import AlbumHandler
from src.utils.fsm import AdminReleaseLvl1


async def change_state(_, __, manager: DialogManager):
    state = manager.dialog_data['doc_state']
    if state is True:
        manager.dialog_data['doc_state'] = False
    else:
        manager.dialog_data['doc_state'] = True


async def task_page_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    user, track, album = await AlbumHandler(data['session_maker'],
                                            data['database_logger']).get_tracks_and_personal_data(
        dialog_manager.dialog_data['user_id'],
        dialog_manager.dialog_data['album_id'])
    doc_id = album.unsigned_license if dialog_manager.dialog_data['doc_state'] is True else album.album_cover
    doc = MediaAttachment(ContentType.DOCUMENT, file_id=MediaId(doc_id))
    logging.info(dialog_manager.event.data)
    return {
        'username': user.tg_username if user.tg_username else user.tg_id,
        'nickname': user.nickname,
        'title': album.album_title,
        'tracks': track,
        'doc': doc
    }


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
    Back(TXT_CONFIRM, id='confirm_unsigned_1', on_click=confirm_release),
    Back(Const('✘ Отклонить'), id='reject_unsigned_1', on_click=reject_release),
    Button(Const('✘ Шаблон'), id='reject_album_template', on_click=coming_soon),
    SwitchTo(Const('✘ Свой ответ'), id='reject_album_custom', state=AdminReleaseLvl1.custom),
    Cancel(TXT_BACK, on_click=cancel_task),
    state=AdminReleaseLvl1.info,
    getter=task_page_getter
)


async def lvl1_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    album = await AlbumHandler(data['session_maker'], data['database_logger']).get_unsigned_state('process')
    logging.info(dialog_manager.event.data)
    return {
        'album': album
    }


choose = Dialog(
    Window(
        Const('Список тасков 1 уровень: \n'
              'Обложка + название + список треков + первичное ЛД'),
        ScrollingGroup(
            Select(
                Format("Релиз №{item.id}"),
                id="alb_adm_track_list",
                items="album",
                item_id_getter=lambda album: album.id,
                on_click=on_task_selected
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
    create_reason_window(AdminReleaseLvl1),
    create_reason_confirm_window(AdminReleaseLvl1, 'unsigned')
)
