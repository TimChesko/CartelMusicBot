from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_dialog import DialogManager
from sqlalchemy.ext.asyncio import AsyncEngine
from structlog._log_levels import BoundLoggerFilteringAtDebug

from src.models.personal_data_template import PersonalDataTemplateHandler
from src.models.tables import PersonalDataTemplate

router = Router()


@router.message(Command(commands="personal_data_template"), flags={'chat_action': 'typing'})
async def cmd_start(msg: Message,
                    engine: AsyncEngine,
                    database_logger: BoundLoggerFilteringAtDebug,
                    dialog_manager: DialogManager):
    data = {
        "passport": {
            "first_name": {
                "type": "Имя",
                "request": "Пришлите ваше - имя",
                "example": "Тимофей",
                "input": [
                    "text"
                ]
            },
            "surname": {
                "type": "Фамилия",
                "request": "Пришлите вашу - фамилию",
                "example": "Лазарев",
                "input": [
                    "text"
                ]
            },
            "middle_name": {
                "type": "Отчество",
                "request": "Пришлите ваше - отчество\nЕсли его нет пришлите в ответ 'нет'",
                "example": "Сергеевич",
                "input": [
                    "text"
                ]
            },
            "passport_series": {
                "type": "Серия паспорта",
                "request": "Пришлите - серию паспорта",
                "example": "1234",
                "input": [
                    "int"
                ]
            },
            "passport_number": {
                "type": "Номер паспорта",
                "request": "Пришлите - номер паспорта",
                "example": "567890",
                "input": [
                    "int"
                ]
            },
            "who_issued_it": {
                "type": "Кем выдан",
                "request": "Пришлите - кем выдан паспорт",
                "example": "ЮВ г.Москва паспортный отдел",
                "input": [
                    "any"
                ]
            },
            "date_of_issue": {
                "type": "Дата выдачи",
                "request": "Выберете - дату выдачи паспорта",
                "example": "07.08.2010",
                "input": [
                    "date"
                ]
            },
            "unit_code": {
                "type": "Код региона",
                "request": "Пришлите - код региона",
                "example": "660-550",
                "input": [
                    "int",
                    "minus"
                ]
            },
            "date_of_birth": {
                "type": "Дата рождения",
                "request": "Выберете - дату рождения",
                "example": "07.09.2003",
                "input": [
                    "date"
                ]
            },
            "place_of_birth": {
                "type": "Место рождения",
                "request": "Пришлите - место рождения",
                "example": "Москва",
                "input": [
                    "text"
                ]
            },
            "registration_address": {
                "type": "Адрес регистрации",
                "request": "Пришлите - адрес регистрации",
                "example": "Москва, ул.Арбат, д.13, кв.110",
                "input": [
                    "any"
                ]
            }
        },
        "bank": {
            "recipient": {
                "type": "ФИО",
                "request": "Пришлите ваше - ФИО",
                "example": "Лазарев Тимофей Сергеевич",
                "input": [
                    "text",
                    "space"
                ]
            },
            "account_code": {
                "type": "Номер счета",
                "request": "Пришлите - номер счета",
                "example": "40217210300013628341",
                "input": [
                    "big_int"
                ]
            },
            "bik_code": {
                "type": "БИК код",
                "request": "Пришлите - банковский идентификационный код",
                "example": "044525974",
                "input": [
                    "big_int"
                ]
            },
            "bank_recipient": {
                "type": "Банк получателя",
                "request": "Пришлите - банк получателя",
                "example": "АО «Тинькофф Банк»",
                "input": [
                    "any"
                ]
            },
            "correct_code": {
                "type": "Корреспондентский счет",
                "request": "Пришлите - корреспондентский счет",
                "example": "30101810145250000974",
                "input": [
                    "int"
                ]
            },
            "inn_code": {
                "type": "ИНН",
                "request": "Пришлите - ИНН",
                "example": "7710341679",
                "input": [
                    "big_int"
                ]
            },
            "kpp_code": {
                "type": "КПП код",
                "request": "Пришлите - код причины постановки на учет (КПП)",
                "example": "771302001",
                "input": [
                    "big_int"
                ]
            }
        }
    }
    for data_type, fields in data.items():
        for field_name, field_data in fields.items():
            type_val = field_data['type']
            request_val = field_data['request']
            example_val = field_data['example']
            input_type_val = ', '.join(field_data['input'])
            personal_data = PersonalDataTemplate(
                header_data=data_type,
                name_data=field_name,
                title=type_val,
                text=request_val,
                example=example_val,
                input_type=input_type_val
            )
            await PersonalDataTemplateHandler(engine, database_logger).add_template(personal_data)
