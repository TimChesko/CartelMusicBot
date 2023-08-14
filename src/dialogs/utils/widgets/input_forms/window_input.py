from datetime import date

from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Format

from src.dialogs.utils.buttons import TXT_BACK
from src.dialogs.utils.calendar import CustomCalendar
from src.utils.fsm import DialogInput


async def start_dialog_filling_profile(
        btn_status: list[bool],
        input_date: bool,
        input_img: bool,
        data: dict,
        manager: DialogManager,
        error: str = None
) -> None:
    """
    Описание функции.
    :param btn_status: Статус кнопок
                       0 - остановка формы
                       1 - назад при вводе текста
                       2 - назад при выборе даты
    :param input_date: Тип формы - ввод текста или даты
    :param input_img: bool
    :param data: Данные для формы
                 text - что будет написано в заголовке
                 correct_input - какие символы можно использовать
    :param manager:
    :param error: текст об ошибке
    :return: None
    """
    data['btn_stop'] = btn_status[0]
    data['btn_back_text'] = btn_status[1]
    data['btn_back_date'] = btn_status[2]
    data['created_text'] = data['text'] if error is None else f"{error}\n\n{data['text']}"
    if input_date:
        await manager.start(state=DialogInput.date, data=data, show_mode=ShowMode.EDIT)
    elif input_img:
        await manager.start(state=DialogInput.img, data=data, show_mode=ShowMode.EDIT)
    else:
        await manager.start(state=DialogInput.text, data=data, show_mode=ShowMode.EDIT)


async def get_data(dialog_manager: DialogManager, **_kwargs):
    start_data = dialog_manager.start_data
    return {
        "text": start_data["created_text"],
        "btn_stop": start_data["btn_stop"],
        "btn_back_text": start_data["btn_back_text"],
        "btn_back_date": start_data["btn_back_date"]
    }


async def save_data(message: Message, _, manager: DialogManager, __):
    start_data = manager.start_data
    await message.delete()
    manager.show_mode = ShowMode.EDIT
    await manager.done(
        [message.text, start_data['data_name'], start_data['title']]
    )


async def save_img(message: Message, _, manager: DialogManager):
    start_data = manager.start_data
    await message.delete()
    manager.show_mode = ShowMode.EDIT
    await manager.done(
        [message.photo[0].file_id, start_data['data_name'], start_data['title']]
    )


async def on_date_selected(_, __, manager: DialogManager, selected_date: date):
    start_data = manager.start_data
    await manager.done([str(selected_date), manager.start_data['data_name'], start_data['title']])


async def on_back(_, __, manager: DialogManager):
    start_data = manager.start_data
    await manager.done(["back", start_data['data_name'], start_data['title']])


dialog_input = Dialog(
    Window(
        Format("{text}"),
        TextInput(
            id=f"input_text",
            on_success=save_data,
        ),
        Button(
            TXT_BACK,
            id="input_text_back",
            on_click=on_back,
            when="btn_back_text"
        ),
        disable_web_page_preview=True,
        state=DialogInput.text,
    ),
    Window(
        Format("{text}"),
        CustomCalendar(
            id=f"input_date",
            on_click=on_date_selected
        ),
        Button(
            TXT_BACK,
            id="input_date_back",
            on_click=on_back,
            when="btn_back_date"
        ),
        disable_web_page_preview=True,
        state=DialogInput.date,
    ),
    Window(
        Format("{text}"),
        MessageInput(
            func=save_img,
            content_types=ContentType.PHOTO
        ),
        Button(
            TXT_BACK,
            id="input_text_back",
            on_click=on_back,
            when="btn_back_text"
        ),
        state=DialogInput.img,
    ),
    getter=get_data
)
