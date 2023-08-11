from aiogram import Bot
from aiogram.enums import ContentType
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, ShowMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Row, Cancel, Back
from aiogram_dialog.widgets.text import Format, Const

from src.dialogs.utils.buttons import TXT_BACK
from src.models.album import AlbumHandler
from src.utils.fsm import AdminReleaseLvl3, AdminReleaseLvl1, AdminReleaseLvl2


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


async def set_reject_reason(msg: Message, _, manager: DialogManager):
    manager.show_mode = ShowMode.EDIT
    if msg.content_type == ContentType.TEXT:
        manager.dialog_data["reason"] = msg.text + '\n'
        await msg.delete()
        await manager.next()
    else:
        await msg.delete()
        manager.dialog_data['title'] = 'Введите текст! ТОЛЬКО ТЕКСТ!'


async def reason_title_getter(dialog_manager: DialogManager, **_kwargs):
    return {'title': dialog_manager.dialog_data.get('title', 'Введи причину отказа в виде текста.')}


async def reason_getter(dialog_manager: DialogManager, **_kwargs):
    return {
        'custom_reason': dialog_manager.dialog_data['reason']
    }


def create_reason_window(state: [AdminReleaseLvl3 | AdminReleaseLvl2 | AdminReleaseLvl1]) -> Window:
    return Window(
        Format('{title}'),
        MessageInput(set_reject_reason),
        SwitchTo(TXT_BACK, state=state.info, id='bck_to_info'),
        state=state.custom,
        getter=reason_title_getter
    )


def create_reason_confirm_window(state: [AdminReleaseLvl3 | AdminReleaseLvl2 | AdminReleaseLvl1], id) -> Window:
    return Window(
        Format('Подтвердите текст:\n'
               '{custom_reason}'),
        Row(
            Cancel(Const("Подтверждаю"), on_click=reject_release, id=f"reason_{id}"),
            Back(Const("Изменить"), id="bck_reason", on_click=clear_reason),
        ),
        SwitchTo(TXT_BACK, state=state.info, id='bck_to_info', on_click=clear_reason),
        state=state.confirm,
        getter=reason_getter
    )
