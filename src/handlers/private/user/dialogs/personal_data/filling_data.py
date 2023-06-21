from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import SwitchTo, Row, Cancel, Back
from aiogram_dialog.widgets.text import Const

from src.utils.fsm import PersonalDataFilling


async def set_firstname(msg: Message, _, manager: DialogManager):
    manager.dialog_data['firstname'] = msg.text
    await manager.next()


async def set_surname(msg: Message, _, manager: DialogManager):
    manager.dialog_data['surname'] = msg.text
    await manager.next()


async def set_middlename(msg: Message, _, manager: DialogManager):
    manager.dialog_data['middlename'] = msg.text
    await manager.next()


async def set_passport_series(msg: Message, _, manager: DialogManager):
    manager.dialog_data['passport_series'] = msg.text
    await manager.next()


async def set_passport_number(msg: Message, _, manager: DialogManager):
    manager.dialog_data['passport_number'] = msg.text
    await manager.next()


async def set_who_issued_it(msg: Message, _, manager: DialogManager):
    manager.dialog_data['who_issued_it'] = msg.text
    await manager.next()


async def set_date_of_issue(msg: Message, _, manager: DialogManager):
    manager.dialog_data['date_of_issue'] = msg.text
    await manager.next()


async def set_unit_code(msg: Message, _, manager: DialogManager):
    manager.dialog_data['unit_code'] = msg.text
    await manager.next()


async def set_date_of_birth(msg: Message, _, manager: DialogManager):
    manager.dialog_data['date_of_birth'] = msg.text
    await manager.next()


async def set_place_of_birth(msg: Message, _, manager: DialogManager):
    manager.dialog_data['place_of_birth'] = msg.text
    await manager.next()


async def set_registration_address(msg: Message, _, manager: DialogManager):
    manager.dialog_data['registration_address'] = msg.text
    await manager.next()


async def set_physical_inn(msg: Message, _, manager: DialogManager):
    manager.dialog_data['physical_inn'] = msg.text
    await manager.next()


async def set_email(msg: Message, _, manager: DialogManager):
    manager.dialog_data['email'] = msg.text
    await manager.next()


async def set_(msg: Message, _, manager: DialogManager, ):
    manager.dialog_data['firstname'] = msg.text
    await manager.next()


filling_data = Dialog(
    Window(
        Const('Добро пожаловать в раздел заполнения личных данных, Вам нужно будет заполнить паспортные и '
              'банковские данные. \n'
              'Для того чтобы начать заполнять данные нажмите "Продолжить"\n'
              'Для того чтобы ознакомиться со всеми нужными документами нажмите "Информация"'),
        Row(
            SwitchTo(
                Const('Информация'), id='data_info', state=PersonalDataFilling.info
            ),
            SwitchTo(
                Const('Продолжить'), id='cont', state=PersonalDataFilling.firstname
            ),
        ),
        Cancel(
            Const('Назад')
        ),
        state=PersonalDataFilling.start
    ),
    Window(
        Const(
            "<b>Личные данные:</b>\n"
            '\nФИО\n'
            'Серия и номер паспорта\n'
            'Кем выдан\n'
            'Дата выдачи\n'
            'Код подразделения\n'
            'Дата рождения\n'
            'Место рождения\n'
            'Адрес регистрации\n'
            'ИНН\n'
            'Адрес электронной почты\n'
            '\n<b>Банковские реквизиты:</b>\n'
            '\nПолучатель\n'
            'Номер счёта\n'
            'БИК\n'
            'Банк-получатель\n'
            'Корр. счет\n'
            'ИНН\n'
            'КПП\n'
            'SWIFT-Код\n'
        ),
        Back(
            Const('Назад'), id='bck2'
        ),
        state=PersonalDataFilling.info,
        parse_mode="HTML"
    ),
    Window(
        Const('Введите имя'),
        MessageInput(set_firstname, content_types=[ContentType.TEXT]),
        Cancel(Const('Отмена')),
        state=PersonalDataFilling.firstname
    ),
    Window(
        Const('Введите фамилию'),
        MessageInput(set_surname, content_types=[ContentType.TEXT]),
        Cancel(Const('Отмена')),
        state=PersonalDataFilling.surname
    ),
    Window(
        Const('Введите отчество'),
        MessageInput(set_middlename, content_types=[ContentType.TEXT]),
        Cancel(Const('Отмена')),
        state=PersonalDataFilling.middlename
    ),
    Window(
        Const('Введите серию паспорта'),
        MessageInput(set_passport_series, content_types=[ContentType.TEXT]),
        Cancel(Const('Отмена')),
        state=PersonalDataFilling.passport_series
    ),
    Window(
        Const('Введите номер паспорта'),
        MessageInput(set_passport_number, content_types=[ContentType.TEXT]),
        Cancel(Const('Отмена')),
        state=PersonalDataFilling.passport_number
    ),
    Window(
        Const('Введите кем выдан паспорт'),
        MessageInput(set_who_issued_it, content_types=[ContentType.TEXT]),
        Cancel(Const('Отмена')),
        state=PersonalDataFilling.who_issued_it
    ),
    Window(
        Const('Введите дату регистрации паспорта'),
        MessageInput(set_date_of_issue, content_types=[ContentType.TEXT]),
        Cancel(Const('Отмена')),
        state=PersonalDataFilling.date_of_issue
    ),
    Window(
        Const('Введите код подразделения'),
        MessageInput(set_unit_code, content_types=[ContentType.TEXT]),
        Cancel(Const('Отмена')),
        state=PersonalDataFilling.unit_code
    ),
    Window(
        Const('Введите дату рождения'),
        MessageInput(set_date_of_birth, content_types=[ContentType.TEXT]),
        Cancel(Const('Отмена')),
        state=PersonalDataFilling.date_of_birth
    ),
    Window(
        Const('Введите место рождения'),
        MessageInput(set_place_of_birth, content_types=[ContentType.TEXT]),
        Cancel(Const('Отмена')),
        state=PersonalDataFilling.place_of_birth
    ),
    Window(
        Const('Введите адрес прописки'),
        MessageInput(set_registration_address, content_types=[ContentType.TEXT]),
        Cancel(Const('Отмена')),
        state=PersonalDataFilling.registration_address
    ),
    Window(
        Const('Введите свой ИНН (как ФИЗ лицо)'),
        MessageInput(set_physical_inn, content_types=[ContentType.TEXT]),
        Cancel(Const('Отмена')),
        state=PersonalDataFilling.physical_inn_code
    ),
    Window(
        Const('Введите свою электронную почту'),
        MessageInput(set_email, content_types=[ContentType.TEXT]),
        Cancel(Const('Отмена')),
        state=PersonalDataFilling.email
    ),
    # Window(
    #     Format('Подтвердите данные:'
    #            '{firstname}'),
    #     state=PersonalDataFilling.finish
    #
    # ),
)
