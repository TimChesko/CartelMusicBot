from datetime import date

from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format, Const

from src.dialogs.profile.personal_data import string
from src.dialogs.utils.calendar import CustomCalendar
from src.utils.fsm import DialogInput


async def start_dialog_filling_profile(
        personal_data: str,
        data_name: str,
        manager: DialogManager,
        error: str = None):
    """
    Запускаем диалог для получение данных ввода
    :param personal_data: passport or bank
    :param data_name: personal data name / example: first_name
    :param manager:
    :param error: send error with text
    :return:
    """
    all_data = string.personal_data[personal_data][data_name]
    data = {"data_type": data_name,
            "request": all_data['request'],
            "example": all_data['example'],
            "error": error}
    if "date" in all_data['input']:
        await manager.start(state=DialogInput.date, data=data)
    else:
        await manager.start(state=DialogInput.text, data=data)


async def get_data(dialog_manager: DialogManager, **_kwargs):
    start_data = dialog_manager.start_data
    # request = start_data["request"] if "error" in start_data \
    #     else f'{start_data["error"]}\n\n{start_data["request"]}'
    return {
        "request": start_data["request"],
        "example": start_data["example"]
    }


async def save_data(message: Message, _, manager: DialogManager, __):
    await manager.done([message.text, manager.start_data['data_type']])


async def on_date_selected(_, __, manager: DialogManager, selected_date: date):
    await manager.done([selected_date, manager.start_data['data_type']])


async def on_back(_, __, manager: DialogManager):
    await manager.done(["back", manager.start_data['data_type']])


dialog_input_text = Dialog(
    Window(
        Format("{request}\n"
               "Пример: {example}"),
        TextInput(id=f"input_text", on_success=save_data),
        Button(Const("< Назад"), id="input_text_back", on_click=on_back),
        state=DialogInput.text,
        getter=get_data
    ),
    Window(
        Format("{request}\n"
               "Пример: {example}"),
        CustomCalendar(id=f"input_date", on_click=on_date_selected),
        Button(Const("< Назад"), id="input_date_back", on_click=on_back),
        state=DialogInput.date,
        getter=get_data
    )
)
