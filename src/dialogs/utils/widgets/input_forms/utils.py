from datetime import datetime
from typing import Any

from aiogram_dialog import DialogManager

from src.models.personal_data_template import PersonalDataTemplateHandler


async def get_data_from_db(header_data: str, manager: DialogManager):
    middleware_data = manager.middleware_data
    data = await PersonalDataTemplateHandler(middleware_data['session_maker'], middleware_data['database_logger']). \
        get_all_args_by_header_data(header_data)
    return await convert_database_to_data(data)


async def convert_database_to_data(data_list: list) -> dict:
    result_dict = {}
    for data in data_list:
        if data["example"] is not None:
            text = data["text"] + "\n\n" + "Пример: " + data["example"]
        else:
            text = data["text"]
        result_dict[data["name_data"]] = {
            'data_name': data["name_data"],
            'title': data["title"],
            'text': text,
            'input_type': data["input_type"].split(",")
        }
    return result_dict


async def convert_data_types(data: dict):
    converted_data = {}
    for key, items in data.items():
        try:
            converted_value = datetime.strptime(str(items), "%Y-%m-%d")
        except ValueError:
            converted_value = items
        converted_data[key] = converted_value
    return converted_data


async def convert_data_type_one(value: Any):
    try:
        converted_value = int(value)
    except ValueError:
        try:
            converted_value = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            converted_value = value
    return converted_value


async def get_key_value(data):
    data_values = {}
    for name_data, items in data.items():
        data_values[name_data] = items["value"]
    return data_values
