import logging
import re

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Window, Dialog, DialogManager, ShowMode
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Cancel, Back
from aiogram_dialog.widgets.text import Const

from src.utils.fsm import Passport


async def data_text(
        message: Message,
        widget: TextInput,
        manager: DialogManager,
        data):
    if re.match(r'^[a-zA-Zа-яА-Я]+$', data) is not None:
        manager.dialog_data[widget.widget_id] = message.text
        await message.delete()
        manager.show_mode = ShowMode.EDIT
        await manager.next()
    else:
        await message.delete()
        await message.answer("Ответ должен быть БЕЗ чисел, знаков и пробелов.\n"
                             "Повторите попытку вновь.")


async def is_numeric_with_minus(text):
    if text.startswith('-') or text.endswith('-'):
        return False
    has_minus = False
    for i, char in enumerate(text):
        if char.isdigit():
            continue
        elif char == '-' and 0 < i < len(text) - 1 and not has_minus and text[i - 1].isdigit() and text[
            i + 1].isdigit():
            has_minus = True
        else:
            return False
    return True


async def data_int(
        message: Message,
        widget: TextInput,
        manager: DialogManager,
        data):
    if await is_numeric_with_minus(data):
        manager.dialog_data[widget.widget_id] = message.text
        await message.delete()
        manager.show_mode = ShowMode.EDIT
        await manager.next()
    else:
        await message.delete()
        await message.answer("Ответ должен быть БЕЗ букв, пробелов и знаков, за исключением '-'.\n"
                             "Пример: 12345 или 111-111\n"
                             "Повторите попытку вновь.")


passport = Dialog(
    Window(
        Const("Перед началом заполнения данных, подготовьте паспорт.\n"
              "Заполнение данных будет состоять из 2 этапов:\n"
              "- ввод данных\n"
              "- прикрепление фотографий"),
        SwitchTo(Const("Продолжить"), id="passport_first_name", state=Passport.first_name),
        Cancel(Const("Вернуться в профиль")),
        state=Passport.add_data
    ),
    Window(
        Const("Пришлите свое имя"),
        TextInput(id="passport_first_name", on_success=data_text),
        state=Passport.first_name
    ),
    Window(
        Const("Пришлите свою фамилию"),
        TextInput(id="passport_surname", on_success=data_text),
        state=Passport.surname
    ),
    Window(
        Const("Пришлите свое отчество или слово 'нет', если его нет"),
        TextInput(id="passport_middle_name", on_success=data_text),
        state=Passport.middle_name
    ),
    Window(
        Const("Пришлите серию паспорта"),
        TextInput(id="passport_passport_series", on_success=data_int),
        state=Passport.passport_series
    ),
    Window(
        Const("Пришлите номер паспорта"),
        TextInput(id="passport_passport_number", on_success=data_int),
        state=Passport.passport_number
    ),
    Window(
        Const("Кем выдан паспорт"),
        TextInput(id="passport_who_issued_it", on_success=data_text),
        state=Passport.who_issued_it
    ),
    # TODO виджет календарь
    Window(
        Const("Дата выдачи паспорта"),
        TextInput(id="passport_date_of_issue", on_success=data_text),
        state=Passport.date_of_issue
    ),
    Window(
        Const("Код подразделения\nПример: 777-777"),
        TextInput(id="passport_unit_code", on_success=data_int),
        state=Passport.unit_code
    ),
    # TODO виджет календарь
    Window(
        Const("Дата вашего рождения"),
        TextInput(id="passport_date_of_birth", on_success=data_text),
        state=Passport.date_of_birth
    ),
    Window(
        Const("Место регистрации"),
        TextInput(id="passport_registration_address", on_success=data_text),
        state=Passport.registration_address
    ),
    Window(
        Const("Проверьте и подтвердите правильность всех данных. "
              "В целях безопасности, в дальнейшем у вас не будет возможности просмотреть"
              " внесенные данные без помощи модераторов."),
        Button(Const("Подтвердить"), id="passport_confirm", on_click=...),
        Back(Const("Назад")),
        state=Passport.confirm
    )
)
