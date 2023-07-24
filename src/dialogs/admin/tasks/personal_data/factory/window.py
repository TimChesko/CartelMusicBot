from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, Row, SwitchTo
from aiogram_dialog.widgets.text import Format, Const

from src.dialogs.utils.buttons import BTN_BACK, TXT_CONFIRM, TXT_REJECT
from src.dialogs.utils.common import on_start_copy_start_data
from src.utils.fsm import PersonalDataCheck


async def start_dialog_check_docs(manager: DialogManager, data: dict):
    if data['no_img'] is True:
        await manager.start(state=PersonalDataCheck.text, data=data)
    else:
        await manager.start(state=PersonalDataCheck.img, data=data)


async def get_data_text(dialog_manager: DialogManager):
    text = dialog_manager.dialog_data['personal_data_text']
    return {
        "text": text,
        "list_answer": "answer"
    }


async def get_data_img(dialog_manager: DialogManager):
    text = dialog_manager.dialog_data['personal_data_text']
    return {
        "text": text,
        "list_answer": "answer"
    }


async def get_data_reject(dialog_manager: DialogManager):
    return {
        "no_img": True
    }


async def on_reject_template(callback: CallbackData, _, manager: DialogManager):
    pass


async def on_reject_edit(msg: Message, _, manager: DialogManager):
    column = manager.dialog_data['column']
    await msg.delete()
    await manager.done({"confirm": False, "column": column, "edit": msg.text, "comment": None})


async def on_reject_comment(msg: Message, _, manager: DialogManager):
    column = manager.dialog_data['column']
    await msg.delete()
    await manager.done({"confirm": False, "column": column, "edit": None, "comment": msg.text})


async def on_confirm(_, __, manager: DialogManager):
    await manager.done({"confirm": True, "column": None, "edit": None, "comment": None})


dialog = Dialog(
    Window(
        Format("{text_info}"),
        Row(
            SwitchTo(Const(TXT_REJECT), id="personal_data_reject", state=PersonalDataCheck.reject_template),
            Button(Const(TXT_CONFIRM), id="personal_data_confirm", on_click=on_confirm)
        ),
        state=PersonalDataCheck.img,
        getter=get_data_img
    ),
    Window(
        Format("{text_info}"),
        Row(
            SwitchTo(Const(TXT_REJECT), id="personal_data_reject", state=PersonalDataCheck.reject_template),
            Button(Const(TXT_CONFIRM), id="personal_data_confirm", on_click=on_confirm)
        ),
        state=PersonalDataCheck.text,
        getter=get_data_text
    ),
    Window(
        Const("Выберете причину отклонения:"),
        Button(Const("Шаблонный ответ"), id="personal_data_reject_template"),
        Button(Const("Написать комментарий"), id="personal_data_reject_comment"),
        Button(Const("Редактировать ответ"), id="personal_data_reject_edit", when="no_img"),
        BTN_BACK,
        state=PersonalDataCheck.reject_template,
        getter=get_data_reject
    ),
    on_start=on_start_copy_start_data,
)
