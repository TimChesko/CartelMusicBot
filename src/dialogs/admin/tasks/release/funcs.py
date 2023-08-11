import logging

from aiogram import Bot
from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import Button

from src.models.album import AlbumHandler


# GETTERS
async def reason_title_getter(dialog_manager: DialogManager, **_kwargs):
    return {'reason_title': dialog_manager.dialog_data.get('reason_title', 'Введи причину отказа в виде текста.')}


async def reason_getter(dialog_manager: DialogManager, **_kwargs):
    return {
        'custom_reason': dialog_manager.dialog_data['reason']
    }


async def task_page_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    user, track, album = await AlbumHandler(data['session_maker'],
                                            data['database_logger']).get_tracks_and_personal_data(
        dialog_manager.dialog_data['user_id'],
        dialog_manager.dialog_data['album_id'])
    content_type = ContentType.DOCUMENT
    doc_id = album.album_cover if dialog_manager.dialog_data.get('doc_state', None) is True else album.unsigned_license
    if album.signed_state == 'process':
        doc_id = album.signed_license
    elif album.mail_track_state == 'process':
        doc_id = album.mail_track_photo
        content_type = ContentType.PHOTO
    doc = MediaAttachment(content_type, file_id=MediaId(doc_id))
    logging.info(dialog_manager.event)
    return {
        'username': user.tg_username if user.tg_username else user.tg_id,
        'nickname': user.nickname,
        'title': album.album_title,
        'tracks': track,
        'doc': doc,
        'checkbox': album.unsigned_state == 'process'
    }


# ON_CLICK
async def confirm_release(callback: CallbackQuery, widget: Button, manager: DialogManager):
    confirm = widget.widget_id.split('_')
    data = manager.middleware_data
    bot: Bot = manager.middleware_data['bot']
    album = await AlbumHandler(data['session_maker'], data['database_logger']).get_album_first(
        manager.dialog_data['album_id'])
    await AlbumHandler(data['session_maker'], data['database_logger']).approve(manager.dialog_data['album_id'],
                                                                               callback.from_user.id,
                                                                               state=confirm[1])
    await bot.send_message(manager.dialog_data['user_id'],
                           f'Ваш релиз "{album.album_title}" прошел проверку, перейдите в меню для подробностей!')


async def reject_release(callback: CallbackQuery, widget: Button, manager: DialogManager):
    reject = widget.widget_id.split('_')
    data = manager.middleware_data
    bot: Bot = manager.middleware_data['bot']
    text = 'Комментарий администратора:\n' + manager.dialog_data.get(
        "reason") if 'reason' in manager.dialog_data else ""
    album = await AlbumHandler(data['session_maker'], data['database_logger']).get_album_first(
        manager.dialog_data['album_id'])
    await AlbumHandler(data['session_maker'], data['database_logger']).reject(manager.dialog_data['album_id'],
                                                                              callback.from_user.id,
                                                                              state=reject[1])
    await bot.send_message(manager.dialog_data['user_id'],
                           f'Ваш релиз "{album.album_title}" не прошел проверку!\n'
                           f'{text}'
                           f'Перейдите в меню для подробностей')


async def on_task_selected(callback: CallbackQuery, __, manager: DialogManager, selected_item):
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


async def cancel_task(_, __, manager: DialogManager):
    data = manager.middleware_data
    await AlbumHandler(data['session_maker'], data['database_logger']).set_task_state(manager.dialog_data['album_id'],
                                                                                      None)
    manager.show_mode = ShowMode.EDIT


async def clear_reason(_, __, manager: DialogManager):
    manager.dialog_data.pop('reason', None)


async def change_state(_, __, manager: DialogManager):
    manager.dialog_data['doc_state'] = not manager.dialog_data['doc_state']


# INPUTS
async def set_reject_reason(msg: Message, _, manager: DialogManager):
    manager.show_mode = ShowMode.EDIT
    if msg.content_type == ContentType.TEXT:
        manager.dialog_data["reason"] = msg.text + '\n'
        await msg.delete()
        await manager.next()
    else:
        await msg.delete()
        manager.dialog_data['reason_title'] = 'Введите текст! ТОЛЬКО ТЕКСТ!'
