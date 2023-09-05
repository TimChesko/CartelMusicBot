import logging

from aiogram import Bot
from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import Button

from src.dialogs.utils.buttons import TxtApprovement
from src.models.release import ReleaseHandler
from src.utils.enums import Status


# GETTERS
async def reason_title_getter(dialog_manager: DialogManager, **_kwargs):
    return {'reason_title': dialog_manager.dialog_data.get('reason_title', 'Введи причину отказа в виде текста.')}


async def reason_getter(dialog_manager: DialogManager, **_kwargs):
    return {
        'custom_reason': dialog_manager.dialog_data['reason']
    }


async def task_page_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    user, track, release, docs = await ReleaseHandler(data['session_maker'],
                                                data['database_logger']).get_tracks_and_personal_data(
        dialog_manager.dialog_data['user_id'],
        dialog_manager.dialog_data['release_id'])
    content_type = ContentType.DOCUMENT
    doc_id = release.release_cover if dialog_manager.dialog_data.get('doc_state',
                                                                     None) is True else release.unsigned_license

    if release.unsigned_status == Status.PROCESS and len(docs) > 1:
        page_number = await dialog_manager.find("stub_scroll").get_page()
        docs.append(release.release_cover)
        logging.info(docs)
        logging.info(page_number)
        all_docs = {number+1: document for number, document in enumerate(docs)}
        logging.info(all_docs)
        doc_id = all_docs[page_number+1]
    elif release.signed_status == Status.PROCESS:
        doc_id = release.signed_license
    elif release.mail_track_status == Status.PROCESS:
        doc_id = release.mail_track_photo
        content_type = ContentType.PHOTO
    doc = MediaAttachment(content_type, file_id=MediaId(doc_id))
    return {
        'username': user.tg_username if user.tg_username else user.tg_id,
        'nickname': user.nickname,
        'title': release.release_title,
        'tracks': track,
        'doc': doc,
        'checkbox': release.unsigned_status == Status.PROCESS,
        'pages': len(docs)
    }


async def unsigned_task_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    user, track, release = await ReleaseHandler(data['session_maker'],
                                                data['database_logger']).get_tracks_and_personal_data(
        dialog_manager.dialog_data['user_id'],
        dialog_manager.dialog_data['release_id'])
    content_type = ContentType.DOCUMENT
    doc_id = release.release_cover if dialog_manager.dialog_data.get('doc_state',
                                                                     None) is True else release[0].unsigned_license
    doc = MediaAttachment(content_type, file_id=MediaId(doc_id))
    return {
        'username': user.tg_username if user.tg_username else user.tg_id,
        'nickname': user.nickname,
        'title': release.release_title,
        'tracks': track,
        'doc': doc,
        'checkbox': release.unsigned_status == Status.PROCESS,
    }

# ON_CLICK
async def confirm_release(callback: CallbackQuery, widget: Button, manager: DialogManager):
    state = widget.widget_id.split('_')[1]
    data = manager.middleware_data
    bot: Bot = manager.middleware_data['bot']
    release = await ReleaseHandler(data['session_maker'], data['database_logger']).get_release(
        manager.dialog_data['release_id'])
    await ReleaseHandler(data['session_maker'], data['database_logger']).approve(manager.dialog_data['release_id'],
                                                                                 callback.from_user.id,
                                                                                 state=state)
    if state == 'mail':
        await bot.send_message(manager.dialog_data['user_id'],
                               TxtApprovement(release.release_title).release_finish())
    else:
        await bot.send_message(manager.dialog_data['user_id'],
                               TxtApprovement(release.release_title).release_approve())


async def reject_release(callback: CallbackQuery, widget: Button, manager: DialogManager):
    state = widget.widget_id.split('_')[1]
    data = manager.middleware_data
    bot: Bot = manager.middleware_data['bot']
    text = 'Причина:\n' + manager.dialog_data.get(
        "reason") if 'reason' in manager.dialog_data else ""
    release = await ReleaseHandler(data['session_maker'], data['database_logger']).get_release(
        manager.dialog_data['release_id'])
    await ReleaseHandler(data['session_maker'], data['database_logger']).reject(manager.dialog_data['release_id'],
                                                                                callback.from_user.id,
                                                                                state=state)
    await bot.send_message(manager.dialog_data['user_id'],
                           TxtApprovement(release.release_title, text).release_reject())


async def on_task_selected(callback: CallbackQuery, __, manager: DialogManager, selected_item):
    item = int(selected_item)
    data = manager.middleware_data
    release = await ReleaseHandler(data['session_maker'], data['database_logger']).get_release(item)
    if release.checker_id is None or release.checker_id == callback.from_user.id:
        await ReleaseHandler(data['session_maker'], data['database_logger']).set_task_state(item,
                                                                                            callback.from_user.id)
        manager.dialog_data['release_id'] = item
        manager.dialog_data['user_id'] = release.user_id
        manager.dialog_data['doc_state'] = True
        await manager.next()
    else:
        await callback.answer('Этот трек уже в работе!')


async def cancel_task(_, __, manager: DialogManager):
    data = manager.middleware_data
    await ReleaseHandler(data['session_maker'], data['database_logger']).set_task_state(
        manager.dialog_data['release_id'],
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
