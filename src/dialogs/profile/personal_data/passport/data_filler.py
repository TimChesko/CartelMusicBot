import logging
import re
from datetime import date
from typing import Any

from aiogram.fsm.state import State
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window, Data
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Back, ManagedCalendarAdapter
from aiogram_dialog.widgets.text import Const

from src.dialogs.profile.personal_data import string
from src.dialogs.profile.personal_data.passport.utils import is_numeric_with_minus, find_data_location
from src.dialogs.utils.calendar import CustomCalendar
from src.models.personal_data import PersonalDataHandler
from src.utils.fsm import Passport, DialogInput


async def data_text(message: Message, widget: TextInput, manager: DialogManager, data):
    await process_data(True, False, False, False, message, widget, manager, data)


async def data_text_punctuation(message: Message, widget: TextInput, manager: DialogManager, data):
    await process_data(True, True, False, False, message, widget, manager, data)


async def data_int_punctuation(message: Message, widget: TextInput, manager: DialogManager, data):
    check = await is_numeric_with_minus(data, False)
    await process_data(False, False, check, False, message, widget, manager, data)


async def data_int(message: Message, widget: TextInput, manager: DialogManager, data):
    check = await is_numeric_with_minus(data, True)
    await process_data(False, False, check, True, message, widget, manager, data)


async def process_data(is_text: bool, text_punctuation: bool,
                       is_int: bool, int_punctuation: bool,
                       message: Message, widget: TextInput,
                       manager: DialogManager, data):
    start_data = manager.start_data
    middleware_data = manager.middleware_data
    user_id = middleware_data['event_from_user'].id
    found_key = start_data.get("profile_edit")
    await message.delete()

    if is_text:
        if re.match(r'^[a-zA-Zа-яА-Я\s,.]+$', data):
            if not text_punctuation and re.match(r'^[a-zA-Zа-яА-Я\s]+$', data):
                return await message.answer("Ответ может содержать буквы и пробелы.\n"
                                            "Повторите попытку снова.")
            if found_key:
                return await update_edit_data(data, manager, message, middleware_data, start_data, user_id)
        else:
            return await message.answer("Ответ может содержать буквы, точки, запитые и пробелы.\n"
                                        "Повторите попытку снова.")
    else:
        if not int_punctuation:
            if is_int:
                return await message.answer("Ответ должен содержать только цифры без пробелов и знаков.\n"
                                            "Пример: 12345\n"
                                            "Повторите попытку снова.")
            else:
                return await message.answer("Ответ должен содержать только цифры без пробелов и знаков, кроме '-'.\n"
                                            "Пример: 12345 или 111-111\n"
                                            "Повторите попытку снова.")
        elif found_key:
            if is_int:
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


async def on_date_selected(callback: CallbackQuery, widget: ManagedCalendarAdapter, manager: DialogManager,
                           selected_date: date):
    start_data = manager.start_data
    middleware_data = manager.middleware_data
    found_key = start_data.get("profile_edit")
    if found_key:
        manager.show_mode = ShowMode.SEND
        return await update_edit_data(selected_date, manager, callback.message,
                                      middleware_data, start_data, middleware_data['event_from_user'].id)
    manager.dialog_data[widget.widget_id] = selected_date.strftime("%Y-%m-%d")
    await manager.next()


async def on_finally_passport(callback: CallbackQuery, _, manager: DialogManager):
    data = manager.middleware_data
    user_id = data['event_from_user'].id
    answer = list(manager.dialog_data.values())
    await PersonalDataHandler(data['engine'], data['database_logger']) \
        .update_all_passport_data(user_id, answer)
    await callback.answer("Вы успешно внесли данные о паспорте !")
    manager.show_mode = ShowMode.SEND
    await manager.done()


async def start_dialog_filling_profile(data_name: str, manager: DialogManager, error: str = None):
    all_data = string.passport
    data = {"data_type": data_name,
            "request": all_data[data_name]['request'],
            "example": all_data[data_name]['example'],
            "error": error}
    if "date" in all_data[data_name]['input']:
        await manager.start(state=DialogInput.date, data=data)
    else:
        await manager.start(state=DialogInput.text, data=data)


async def create_task_list(_, __, manager: DialogManager):
    all_data = string.passport
    tasks = []
    for i in all_data:
        tasks.append(i)
    manager.dialog_data["task_list"] = tasks
    await start_dialog_filling_profile(tasks[0], manager)


async def process_input(input_result: str, input_type: list, manager: DialogManager):

    template_input = {
        "int": ["0-9", "цифры"],
        "punctuation": [",.", "точки, запятые"],
        "minus": ["-", "тире"],
        "text": ["a-zA-Zа-яА-Я", "буквы"],
        "space": ["\s", "пробелы"],
        "any": [".*", "любые символы"]
    }

    input_pattern = ""
    list_use = []
    for item in input_type:
        input_pattern += template_input.get(item, [""])[0]
        list_use.append(template_input.get(item, [""])[1])

    use_s = ", ".join(list_use)
    if "any" in input_type:
        regex_pattern = rf'{input_pattern}$'
    else:
        regex_pattern = rf'^[{input_pattern}]+$'

    logging.info(regex_pattern)
    if re.match(regex_pattern, input_result[0]):
        logging.info("Добавили в бд")
        manager.dialog_data["task_list"].pop(0)
        if len(manager.dialog_data["task_list"]) != 0:
            await start_dialog_filling_profile(manager.dialog_data["task_list"][0], manager)
        else:
            await manager.switch_to(Passport.confirm)
    else:
        error = f"Ответ может содержать {use_s}\nПовторите попытку снова"
        await start_dialog_filling_profile(manager.dialog_data["task_list"][0], manager, error)





async def process_result(_, result: Any, manager: DialogManager):
    if "task_list" in manager.dialog_data:
        all_data = string.passport
        await process_input(result, all_data[result[1]]['input'], manager)
    else:
        await manager.done()


passport = Dialog(
    Window(
        Const("Перед началом заполнения данных, подготовьте паспорт.\n"
              "Заполнение данных будет состоять из 2 этапов:\n"
              "- ввод данных\n"
              "- прикрепление фотографий"),
        Button(
            Const("Продолжить"),
            id="passport_start",
            on_click=create_task_list
        ),
        Cancel(Const("Вернуться в профиль")),
        state=Passport.add_data
    ),
    # Window(
    #     Const(f"{string.passport['first_name']['request']}\n"
    #           f"Пример: {string.passport['first_name']['example']}"),
    #     TextInput(id="passport_first_name", on_success=data_text),
    #     state=Passport.first_name
    # ),
    # Window(
    #     Const(f"{string.passport['surname']['request']}\n"
    #           f"Пример: {string.passport['surname']['example']}"),
    #     TextInput(id="passport_surname", on_success=data_text),
    #     state=Passport.surname
    # ),
    # Window(
    #     Const(f"{string.passport['middle_name']['request']}\n"
    #           f"Пример: {string.passport['middle_name']['example']}"),
    #     TextInput(id="passport_middle_name", on_success=data_text),
    #     state=Passport.middle_name
    # ),
    # Window(
    #     Const(f"{string.passport['passport_series']['request']}\n"
    #           f"Пример: {string.passport['passport_series']['example']}"),
    #     TextInput(id="passport_passport_series", on_success=data_int),
    #     state=Passport.passport_series
    # ),
    # Window(
    #     Const(f"{string.passport['passport_number']['request']}\n"
    #           f"Пример: {string.passport['passport_number']['example']}"),
    #     TextInput(id="passport_passport_number", on_success=data_int),
    #     state=Passport.passport_number
    # ),
    # Window(
    #     Const(f"{string.passport['who_issued_it']['request']}\n"
    #           f"Пример: {string.passport['who_issued_it']['example']}"),
    #     TextInput(id="passport_who_issued_it", on_success=data_text_punctuation),
    #     state=Passport.who_issued_it
    # ),
    # Window(
    #     Const(f"{string.passport['date_of_issue']['request']}\n"),
    #     CustomCalendar(
    #         id="passport_date_of_issue",
    #         on_click=on_date_selected,
    #     ),
    #     state=Passport.date_of_issue
    # ),
    # Window(
    #     Const(f"{string.passport['unit_code']['request']}\n"
    #           f"Пример: {string.passport['unit_code']['example']}"),
    #     TextInput(id="passport_unit_code", on_success=data_int_punctuation),
    #     state=Passport.unit_code
    # ),
    # Window(
    #     Const(f"{string.passport['date_of_birth']['request']}\n"),
    #     CustomCalendar(
    #         id="passport_date_of_birth",
    #         on_click=on_date_selected,
    #     ),
    #     state=Passport.date_of_birth
    # ),
    # Window(
    #     Const(f"{string.passport['place_of_birth']['request']}\n"
    #           f"Пример: {string.passport['place_of_birth']['example']}"),
    #     TextInput(id="passport_place_of_birth", on_success=data_text_punctuation),
    #     state=Passport.place_of_birth
    # ),
    # Window(
    #     Const(f"{string.passport['registration_address']['request']}\n"
    #           f"Пример: {string.passport['registration_address']['example']}"),
    #     TextInput(id="passport_registration_address", on_success=data_text_punctuation),
    #     state=Passport.registration_address
    # ),
    Window(
        Const("Проверьте и подтвердите правильность всех данных. "
              "В целях безопасности, в дальнейшем у вас не будет возможности просмотреть"
              " внесенные данные без помощи модераторов."),
        Button(Const("Подтвердить"), id="passport_confirm", on_click=on_finally_passport),
        Back(Const("Назад")),
        state=Passport.confirm
    ),
    on_process_result=process_result,
)
