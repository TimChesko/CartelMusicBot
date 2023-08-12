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
        result_dict[data["name_data"]] = {
            'data_name': data["name_data"],
            'title': data["title"],
            'text': data["text"] + "\n\n" + "Пример: " + data["example"],
            'input_type': data["input_type"].split(",")
        }
    return result_dict


async def convert_data_types(data: dict):
    converted_data = {}
    for key, value in data.items():
        # Попытка конвертировать в дату формата %Y-%m-%d
        try:
            converted_value = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            # Если не удалось выполнить конвертацию, оставляем значение без изменений
            converted_value = value
        converted_data[key] = converted_value
    return converted_data


async def convert_data_type_one(value: Any):
    # Попытка конвертировать в число
    try:
        converted_value = int(value)
    except ValueError:
        # Попытка конвертировать в дату формата %Y-%m-%d
        try:
            converted_value = datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            # Если не удалось выполнить конвертацию, оставляем значение без изменений
            converted_value = value
    return converted_value
