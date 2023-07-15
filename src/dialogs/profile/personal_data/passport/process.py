import re
from typing import Any

from aiogram_dialog import DialogManager

from src.dialogs.profile.personal_data import string
from src.dialogs.profile.personal_data.passport.input_factory import start_dialog_filling_profile


async def save_task_list_and_start(personal_data: str, task_list: list, manager: DialogManager):
    manager.dialog_data['save_input'] = {}
    manager.dialog_data["personal_data"] = personal_data
    manager.dialog_data["task_list_start"] = []
    manager.dialog_data["task_list_end"] = task_list
    await start_dialog_filling_profile(personal_data, task_list[0], manager)


async def process_result(_, result: Any, manager: DialogManager):
    dialog_data = manager.dialog_data
    task_list_start = dialog_data["task_list_start"]
    task_list_end = dialog_data["task_list_end"]
    personal_data = dialog_data["personal_data"]

    if "back" == result[0]:
        if len(task_list_start) != 0:
            task_list_end.insert(0, task_list_start.pop())
            await start_dialog_filling_profile(personal_data, task_list_end[0], manager)
        else:
            await manager.done()
    elif "task_list_end" in manager.dialog_data:
        all_data = string.personal_data
        await process_input(result, all_data[personal_data][result[1]]['input'], manager)
    else:
        await manager.next()


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
        input_pattern += template_input.get(item, [""])[0]
        list_use.append(template_input.get(item, [""])[1])

    use_s = ", ".join(list_use)
    if "any" in input_type:
        regex_pattern = rf'{input_pattern}$'
    else:
        regex_pattern = rf'^[{input_pattern}]+$'

    if "date" in input_type or re.match(regex_pattern, input_result[0]):
        old_item = manager.dialog_data["task_list_end"].pop(0)
        if "date" in input_type:
            date = input_result[0]
            manager.dialog_data['save_input'][old_item] = date.strftime("%Y-%m-%d")
        else:
            manager.dialog_data['save_input'][old_item] = input_result[0]
        manager.dialog_data["task_list_start"].append(old_item)
        if len(manager.dialog_data["task_list_end"]) != 0:
            await start_dialog_filling_profile(
                manager.dialog_data["personal_data"],
                manager.dialog_data["task_list_end"][0],
                manager)
        else:
            await manager.next()
    else:
        error = f"Ответ может содержать {use_s}\nПовторите попытку снова"
        await start_dialog_filling_profile(
            manager.dialog_data["personal_data"],
            manager.dialog_data["task_list_end"][0],
            manager, error)
