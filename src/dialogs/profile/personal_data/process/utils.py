from datetime import datetime
from typing import Any


async def convert_data_types(data: dict):
    converted_data = {}
    for key, value in data.items():
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
