import logging
import re

from aiogram_dialog import DialogManager

from src.dialogs.profile.personal_data import string
from src.dialogs.profile.personal_data.passport.edit import update_edit_data
from src.utils.fsm import DialogInput


async def find_data_location(data):
    if data in string.passport:
        return "password"
    elif data in string.bank:
        return "bank"
    else:
        return ""


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


async def process_input(input_result: str, input_type: list, manager: DialogManager):
    template_input = {
        "int": ["0-9", "цифры"],
        "punctuation": [",.", "точки, запятые"],
        "minus": ["-", "тире"],
        "text": ["a-zA-Zа-яА-Я", "буквы"],
        "space": ["\s", "пробелы"],
        "any": [".*", "любые символы"],
        "date": [".*", "любое число"],
    }

    input_pattern = ""
    list_use = []
    for item in input_type:
        logging.info(item)
        input_pattern += template_input.get(item, [""])[0]
        list_use.append(template_input.get(item, [""])[1])

    use_s = ", ".join(list_use)
    if "any" in input_type:
        regex_pattern = rf'{input_pattern}$'
    else:
        regex_pattern = rf'^[{input_pattern}]+$'

    if "date" in input_type or re.match(regex_pattern, input_result[0]):
        # TODO сохранять в дату диалога, затем пачкой выгрузить
        manager.dialog_data["task_list_start"].append(manager.dialog_data["task_list_end"].pop(0))
        if len(manager.dialog_data["task_list_end"]) != 0:
            await start_dialog_filling_profile(manager.dialog_data["task_list_end"][0], manager)
        else:
            await manager.next()
    else:
        error = f"Ответ может содержать {use_s}\nПовторите попытку снова"
        await start_dialog_filling_profile(manager.dialog_data["task_list_end"][0], manager, error)
