from aiogram.types import CallbackQuery, Message
from aiogram_dialog import (
    Dialog, DialogManager, Window, StartMode, ShowMode,
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Row, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.models.employee import EmployeeHandler
from src.utils.fsm import AdminRegistration, AdminMenu


async def fullname_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.dialog_data
    return {
        'fullname': f'{data["first_name"]} {data["surname"]} {data["middle_name"]}'
    }


async def set_info(message: Message, widget: TextInput, dialog_manager: DialogManager, _):
    dialog_manager.dialog_data[widget.widget_id] = message.text
    dialog_manager.show_mode = ShowMode.EDIT
    await message.delete()
    await dialog_manager.next()


async def on_finish(callback: CallbackQuery, _, manager: DialogManager):
    data = manager.middleware_data
    first_name, surname, middle_name = manager.dialog_data['first_name'], manager.dialog_data['surname'], \
        manager.dialog_data['middle_name']
    await EmployeeHandler(data['session_maker'], data['database_logger']).set_fullname(callback.from_user.id,
                                                                                       first_name, surname, middle_name)
    await manager.start(state=AdminMenu.start, mode=StartMode.RESET_STACK, show_mode=ShowMode.EDIT)


reg_fullname = Dialog(
    Window(
        Const('Перед тем как работать через бота, нужно пройти короткую регистрацию.'),
        Const('Введите свое имя:'),
        TextInput(id='first_name', on_success=set_info),
        state=AdminRegistration.first_name
    ),
    Window(
        Const('Введите свою фамилию:'),
        TextInput(id='surname', on_success=set_info),
        state=AdminRegistration.surname
    ),
    Window(
        Const('Введите свою отчество:'),
        TextInput(id='middle_name', on_success=set_info),
        state=AdminRegistration.middle_name
    ),
    Window(
        Format('Вас зовут {fullname}, Вы уверены?'),
        Row(
            SwitchTo(Const('Сомневаюсь...'), id='doubt', state=AdminRegistration.first_name),
            Button(Const('Уверен'), id='success', on_click=on_finish),
        ),
        state=AdminRegistration.confirm,
        getter=fullname_getter
    ),
)
