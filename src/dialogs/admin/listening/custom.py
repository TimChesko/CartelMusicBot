from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Row, Button, Back, SwitchTo
from aiogram_dialog.widgets.text import Format, Const

from src.data import config
from src.models.tracks import TrackHandler
from src.models.user import UserHandler
from src.utils.fsm import RejectAnswer, AdminListening


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


async def on_finish_custom_reason(callback: CallbackQuery, _, manager: DialogManager):
    data = manager.middleware_data
    track_id = manager.dialog_data['getter_info']
    reason = manager.dialog_data['reason']
    await data['bot'].send_message()
    await manager.done()


reason_window = Window(
    Format('#{track_id} -- Введи причину отказа'),
    MessageInput(set_reject_reason, content_types=[ContentType.TEXT]),
    MessageInput(other_type_handler_text),
    SwitchTo(Const('Отмена'), state=AdminListening.info, id='bck_to_info'),
    state=RejectAnswer.start,
    getter=id_getter
),
confirm_reason_window = Window(
    Format('Подтвердите текст:\n'
           '{custom_reason}'),
    Row(
        Button(Const("Подтверждаю"), on_click=on_finish_custom_reason, id="approve_reason"),
        Back(Const("Изменить"), id="bck_reason"),
    ),
    SwitchTo(Const('Отмена'), state=AdminListening.info, id='bck_to_info'),
    state=RejectAnswer.finish,
    getter=reason_getter
)
