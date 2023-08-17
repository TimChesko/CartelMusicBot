from aiogram.types import CallbackQuery, Message
from aiogram_dialog import (
    Dialog, DialogManager, Window, StartMode, ShowMode,
)
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.input.text import ManagedTextInputAdapter
from aiogram_dialog.widgets.kbd import Button, Row, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.utils.buttons import TXT_APPROVE, TXT_BACK
from src.models.employee import EmployeeHandler
from src.utils.fsm import AdminRegistration, AdminMenu


async def answer(msg: Message, __, dialog_manager: DialogManager, _):
    data = dialog_manager.middleware_data
    await EmployeeHandler(data['session_maker'], data['database_logger']).add_new_employee(msg)
    admins = await EmployeeHandler(data['session_maker'], data['database_logger']).get_admins()
    if admins:
        for admin in admins:
            await msg.bot.send_message(admin, f'❗️Новый пользователь❗️\n'
                                              f' ID: {msg.from_user.id}\n'
                                              f' username: @{msg.from_user.username}\n'
                                              f' firstname: {msg.from_user.first_name}\n'
                                              f' lastname: {msg.from_user.last_name}')
    await dialog_manager.next()


async def fullname_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.dialog_data
    return {
        'fullname': f'{data["surname"]} {data["first_name"]} {data["middle_name"]}'
    }


async def set_info(message: Message, widget: ManagedTextInputAdapter, dialog_manager: DialogManager, _):
    dialog_manager.dialog_data[widget.widget_id] = message.text
    dialog_manager.show_mode = ShowMode.EDIT
    await message.delete()
    await dialog_manager.next()


async def on_finish(callback: CallbackQuery, _, manager: DialogManager):
    data = manager.middleware_data
    fullname = f"{manager.dialog_data['first_name']} {manager.dialog_data['surname']} {manager.dialog_data['middle_name']}"
    await EmployeeHandler(data['session_maker'], data['database_logger']).set_fullname(callback.from_user.id,
                                                                                       fullname)
    await manager.start(state=AdminMenu.start, mode=StartMode.RESET_STACK, show_mode=ShowMode.EDIT)


reg_fullname = Dialog(
    Window(
        Const('🔰 Перед тем как работать через бота, нужно пройти короткую регистрацию.\n'),
        Const('1️⃣ Пришлите своё - <b>имя</b>'),
        TextInput(id='first_name', on_success=set_info),
        state=AdminRegistration.first_name
    ),
    Window(
        Const('2️⃣ Пришлите свою - <b>фамилию</b>'),
        TextInput(id='surname', on_success=set_info),
        state=AdminRegistration.surname
    ),
    Window(
        Const('3️⃣ Пришлите своё - <b>отчество</b>'),
        TextInput(id='middle_name', on_success=set_info),
        state=AdminRegistration.middle_name
    ),
    Window(
        Format('Вас зовут <b>{fullname}</b> ?'),
        Row(
            SwitchTo(TXT_BACK, id='restart_reg', state=AdminRegistration.first_name),
            Button(TXT_APPROVE, id='success', on_click=on_finish),
        ),
        state=AdminRegistration.confirm,
        getter=fullname_getter
    )
)
