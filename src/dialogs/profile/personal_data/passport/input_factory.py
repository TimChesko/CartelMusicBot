from datetime import date

from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.text import Format

from src.dialogs.utils.calendar import CustomCalendar
from src.utils.fsm import DialogInput


async def get_data(dialog_manager: DialogManager, **_kwargs):
    start_data = dialog_manager.start_data
    request = start_data["request"] if start_data["error"] is None \
        else f'{start_data["error"]}\n\n{start_data["request"]}'
    return {
        "request": request,
        "example": start_data["example"]
    }


async def save_data(message: Message, _, manager: DialogManager, __):
    await manager.done([message.text, manager.start_data['data_type']])


dialog_input_text = Dialog(
    Window(
        Format("{request}\n"
               "Пример: {example}"),
        TextInput(id=f"input_text", on_success=save_data),
        state=DialogInput.text,
        getter=get_data
    )
)


async def on_date_selected(_, __, manager: DialogManager, selected_date: date):
    await manager.done([selected_date, manager.start_data['data_type']])


dialog_input_date = Dialog(
    Window(
        Format("{request}\n"
               "Пример: {example}"),
        CustomCalendar(id=f"input_date", on_click=on_date_selected),
        state=DialogInput.date,
        getter=get_data
    )
)
