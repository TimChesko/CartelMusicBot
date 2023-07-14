import logging
import re
from datetime import date

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Window, Dialog, DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Cancel, Back, ManagedCalendarAdapter
from aiogram_dialog.widgets.text import Const

from src.dialogs.profile.personal_data import string
from src.dialogs.utils.calendar import CustomCalendar
from src.models.personal_data import PersonalDataHandler
from src.utils.fsm import Passport


async def data_text(message: Message, widget: TextInput, manager: DialogManager, data):
    await data_process(True, False, False, message, widget, manager, data)


async def data_int_minus(message: Message, widget: TextInput, manager: DialogManager, data):
    check = await is_numeric_with_minus(data, False)
    await data_process(False, check, False, message, widget, manager, data)


async def data_int_without_minus(message: Message, widget: TextInput, manager: DialogManager, data):
    check = await is_numeric_with_minus(data, True)
    await data_process(False, check, True, message, widget, manager, data)


async def is_numeric_with_minus(text, is_int: bool):
    if text.startswith('-') or text.endswith('-'):
        return False
    has_minus = False
    for i, char in enumerate(text):
        if char.isdigit():
            continue
        elif char == '-' and 0 < i < len(text) - 1 \
                and not has_minus and text[i - 1].isdigit() \
                and text[i + 1].isdigit():
            has_minus = True
            if is_int:
                return False
        else:
            return False
    return True


async def find_data_location(data):
    if data in string.passport:
        return "password"
    elif data in string.bank:
        return "bank"
    else:
        return ""


async def data_process(is_text: bool, checker: bool, type_int: bool,
                       message: Message, widget: TextInput,
                       manager: DialogManager, data):
    start_data = manager.start_data
    middleware_data = manager.middleware_data
    user_id = middleware_data['event_from_user'].id
    found_key = start_data.get("profile_edit")
    await message.delete()

    if is_text:
        if re.match(r'^[a-zA-Zа-яА-Я\s]+$', data):
            if found_key:
                return await update_edit_data(data, manager, message, middleware_data, start_data, user_id)
        else:
            return await message.answer("Ответ должен содержать только буквы и пробелы.\n"
                                        "Повторите попытку снова.")
    else:
        if not checker:
            if type_int:
                await message.answer("Ответ должен содержать только цифры без пробелов и знаков.\n"
                                     "Пример: 12345\n"
                                     "Повторите попытку снова.")
            else:
                await message.answer("Ответ должен содержать только цифры без пробелов и знаков, кроме '-'.\n"
                                     "Пример: 12345 или 111-111\n"
                                     "Повторите попытку снова.")
            return
        elif found_key:
            if type_int:
                data = int(data)
            return await update_edit_data(data, manager, message, middleware_data, start_data, user_id)

    manager.dialog_data[widget.widget_id] = message.text
    manager.show_mode = ShowMode.EDIT
    await manager.next()


async def update_edit_data(data, manager, message, middleware_data, start_data, user_id):
    location = await find_data_location(start_data['profile_edit'])
    answer = await PersonalDataHandler(middleware_data['engine'], middleware_data['database_logger']). \
        update_personal_data(user_id, start_data['profile_edit'], data, location, start_data['count_edit'])
    if answer:
        await message.answer("Вы успешно внесли изменения!")
    else:
        await message.answer("Произошла ошибка")
    await manager.done()


async def on_date_selected(callback: CallbackQuery, widget: ManagedCalendarAdapter, manager: DialogManager, selected_date: date):
    start_data = manager.start_data
    middleware_data = manager.middleware_data
    found_key = start_data.get("profile_edit")
    if found_key:
        manager.show_mode = ShowMode.SEND
        return await update_edit_data(selected_date, manager, callback.message,
                                      middleware_data, start_data, middleware_data['event_from_user'].id)
    manager.dialog_data[widget.widget_id] = selected_date.strftime("%Y-%m-%d")
    await manager.next()


async def on_finally(callback: CallbackQuery, _, manager: DialogManager):
    data = manager.middleware_data
    user_id = data['event_from_user'].id
    answer = list(manager.dialog_data.values())
    await PersonalDataHandler(data['engine'], data['database_logger']) \
        .update_all_passport_data(user_id, answer)
    await callback.answer("Вы успешно внесли данные о паспорте !")
    manager.show_mode = ShowMode.SEND
    await manager.done()


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
        TextInput(id="passport_passport_series", on_success=data_int_without_minus),
        state=Passport.passport_series
    ),
    Window(
        Const("Пришлите номер паспорта"),
        TextInput(id="passport_passport_number", on_success=data_int_without_minus),
        state=Passport.passport_number
    ),
    Window(
        Const("Кем выдан паспорт"),
        TextInput(id="passport_who_issued_it", on_success=data_text),
        state=Passport.who_issued_it
    ),
    Window(
        Const("Дата выдачи паспорта"),
        CustomCalendar(
            id="passport_date_of_issue",
            on_click=on_date_selected,
        ),
        state=Passport.date_of_issue
    ),
    Window(
        Const("Код подразделения\nПример: 777-777"),
        TextInput(id="passport_unit_code", on_success=data_int_minus),
        state=Passport.unit_code
    ),
    Window(
        Const("Дата вашего рождения"),
        CustomCalendar(
            id="passport_date_of_birth",
            on_click=on_date_selected,
        ),
        state=Passport.date_of_birth
    ),
    Window(
        Const("Место рождения\nПример: Москва"),
        TextInput(id="passport_place_of_birth", on_success=data_text),
        state=Passport.place_of_birth
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
        Button(Const("Подтвердить"), id="passport_confirm", on_click=on_finally),
        Back(Const("Назад")),
        state=Passport.confirm
    )
)
