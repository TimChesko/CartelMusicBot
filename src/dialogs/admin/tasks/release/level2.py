import logging

from aiogram import Bot
from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Back, Cancel, Checkbox, SwitchTo, Row, Button
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format, List

from src.dialogs.admin.tasks.release.level1 import reject_template
from src.dialogs.utils.buttons import BTN_CANCEL_BACK, TXT_CONFIRM, TXT_BACK
from src.models.album import AlbumHandler
from src.utils.fsm import AdminReleaseLvl1, AdminReleaseLvl2


async def reject(callback: CallbackQuery, __, manager: DialogManager):
    data = manager.middleware_data
    bot: Bot = manager.middleware_data['bot']
    await AlbumHandler(data['session_maker'], data['database_logger']).reject(manager.dialog_data['album_id'],
                                                                              callback.from_user.id,
                                                                              state='signed')
    text = manager.dialog_data.get("reason") if manager.dialog_data.get("reason") else "Комментарий отсутствует"
    await bot.send_message(manager.dialog_data['user_id'],
                           f'Ваш Лиц. Договор отклонен с комментарием:\n'
                           f'{text}'
                           f' \n перейдите в меню для дальнейших действий')


async def reason_getter(dialog_manager: DialogManager, **_kwargs):
    return {
        'custom_reason': dialog_manager.dialog_data['reason']
    }


async def set_reject_reason(msg: Message, _, manager: DialogManager):
    manager.dialog_data["reason"] = msg.text
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    await manager.next()


async def other_type_handler_text(msg: Message, _, __):
    await msg.answer("Напишите причину в виде текста")


reason_window = Window(
    Const('Введи причину отказа'),
    MessageInput(set_reject_reason, content_types=[ContentType.TEXT]),
    MessageInput(other_type_handler_text),
    SwitchTo(TXT_BACK, state=AdminReleaseLvl2.info, id='bck_to_info'),
    state=AdminReleaseLvl2.custom,
    getter={}
)
confirm_reason_window = Window(
    Format('Подтвердите текст:\n'
           '{custom_reason}'),
    Row(
        Cancel(Const("Подтверждаю"), on_click=reject, id="approve_reason"),
        Back(Const("Изменить"), id="bck_reason"),
    ),
    SwitchTo(TXT_BACK, state=AdminReleaseLvl2.info, id='bck_to_info'),
    state=AdminReleaseLvl2.confirm,
    getter=reason_getter
)


async def confirm_album(callback: CallbackQuery, __, manager: DialogManager):
    data = manager.middleware_data
    bot: Bot = manager.middleware_data['bot']
    await AlbumHandler(data['session_maker'], data['database_logger']).approve(manager.dialog_data['album_id'],
                                                                               callback.from_user.id,
                                                                               state='signed')
    await bot.send_message(manager.dialog_data['user_id'],
                           'Ваш Лиц. Договор одобрен, перейдите в меню для дальнейших действий')


async def cancel_task(_, __, manager: DialogManager):
    data = manager.middleware_data
    await AlbumHandler(data['session_maker'], data['database_logger']).set_task_state(manager.dialog_data['album_id'],
                                                                                      None)
    manager.show_mode = ShowMode.EDIT


async def task_page_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    user, track, album = await AlbumHandler(data['session_maker'],
                                            data['database_logger']).get_tracks_and_personal_data(
        dialog_manager.dialog_data['user_id'],
        dialog_manager.dialog_data['album_id'])
    doc = MediaAttachment(ContentType.DOCUMENT, file_id=MediaId(album.signed_license))
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
    Back(TXT_CONFIRM, id='approve_album', on_click=confirm_album),
    Back(Const('✘ Отклонить'), id='reject_album', on_click=reject),
    Button(Const('✘ Шаблон'), id='reject_album_template', on_click=reject_template),
    SwitchTo(Const('✘ Свой ответ'), id='reject_album_custom', state=AdminReleaseLvl2.custom),
    Cancel(TXT_BACK, on_click=cancel_task),
    state=AdminReleaseLvl2.info,
    getter=task_page_getter
)


async def lvl2_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    album = await AlbumHandler(data['session_maker'], data['database_logger']).get_signed_state('process')
    logging.info(album)
    return {
        'album': album
    }


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
        await manager.switch_to(AdminReleaseLvl2.start)


choose = Dialog(
    Window(
        Const('Список тасков 2 уровень: \n'
              'Подписанное ЛД, проверяй подпись'),
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
            id='scroll_albums_lvl2',
            hide_on_single_page=True
        ),
        BTN_CANCEL_BACK,
        state=AdminReleaseLvl2.start,
        getter=lvl2_getter
    ),
    task_page,
    reason_window,
    confirm_reason_window
)
