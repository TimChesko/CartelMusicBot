from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Row, Button, Back
from aiogram_dialog.widgets.text import Format, Const

from src.data import config
from src.keyboards.inline.listening import markup_new_listening, markup_edit_listening
from src.models.tracks import TrackHandler
from src.models.user import UserHandler
from src.utils.fsm import RejectAnswer


async def id_getter(dialog_manager: DialogManager, **kwargs):
    return {
        'track_id': dialog_manager.start_data['track_id']
    }


async def reason_getter(dialog_manager: DialogManager, **kwargs):
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


async def break_answer(callback: CallbackQuery, _, manager: DialogManager):
    data = manager.middleware_data
    track_id = manager.start_data['track_id']
    msg_id = manager.start_data['msg_id']
    chat_id = config.CHATS_BACKUP[0]  # TODO нужный чат
    if manager.start_data['state'] == 'new':
        await data['bot'].edit_message_reply_markup(chat_id, msg_id, reply_markup=markup_new_listening(track_id))
    else:
        await data['bot'].edit_message_reply_markup(chat_id, msg_id, reply_markup=markup_edit_listening(track_id))


async def on_finish_custom_reason(callback: CallbackQuery, _, manager: DialogManager):
    data = manager.middleware_data
    chat_id = config.CHATS_BACKUP[0]  # TODO нужный чат
    track_id = int(manager.start_data['track_id'])
    msg_id = manager.start_data['msg_id']
    user_id, title = await TrackHandler(data['engine'], data['database_logger']).get_custom_answer_info_by_id(
        track_id)
    nickname, username = await UserHandler(data['engine'], data['database_logger']).get_nicknames_by_tg_id(user_id)
    reason = manager.dialog_data['reason']
    if manager.start_data['state'] == 'new':
        await data['bot'].edit_message_caption(chat_id=chat_id,
                                               message_id=msg_id,
                                               caption=f'⛔️ОТКЛОНЕНО⛔️ \n'
                                                       f'Серийный номер: #{track_id} \n'
                                                       f'Причина: {reason} \n'
                                                       f'Трек: "{title}" \n'
                                                       f'Артист: {nickname} / @{username} \n'
                                                       f'Отклонил: {callback.from_user.id} / @{callback.from_user.username}')
    else:
        await data['bot'].edit_message_caption(chat_id=chat_id,
                                               message_id=msg_id,
                                               caption=f'ПОВТОРНОЕ ПРОСЛУШИВАНИЕ'
                                                       f'⛔️ОТКЛОНЕНО⛔️ \n'
                                                       f'Серийный номер: #{track_id} \n'
                                                       f'Причина: {reason} \n'
                                                       f'Трек: "{title}" \n'
                                                       f'Артист: {nickname} / @{username} \n'
                                                       f'Отклонил: {callback.from_user.id} / @{callback.from_user.username}')
    await TrackHandler(data['engine'], data['database_logger']).set_new_status_track(track_id, 'reject',
                                                                                     callback.from_user.id)
    await data['bot'].send_message(user_id, f'Ваш трек "{title}" отклонен с комментарием: \n'
                                            f'{reason}')
    await manager.done()


custom_answer = Dialog(
    Window(
        Format('#{track_id} -- Введи причину отказа'),
        MessageInput(set_reject_reason, content_types=[ContentType.TEXT]),
        MessageInput(other_type_handler_text),
        Cancel(Const('Отмена'), on_click=break_answer),
        state=RejectAnswer.start,
        getter=id_getter
    ),
    Window(
        Format('Подтвердите текст:\n'
               '{custom_reason}'),
        Row(
            Button(Const("Подтверждаю"), on_click=on_finish_custom_reason, id="approve_reason"),
            Back(Const("Изменить"), id="bck_reason"),
        ),
        Cancel(Const("Отмена"), on_click=break_answer),
        state=RejectAnswer.finish,
        getter=reason_getter
    ),
)
