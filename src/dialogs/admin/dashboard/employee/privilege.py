import logging

from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Cancel, Button, Row, Back, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.data import config
from src.dialogs.admin.common import translate_privilege
from src.dialogs.admin.dashboard.employee.add import developer_getter
from src.models.employee import EmployeeHandler
from src.models.user import UserHandler
from src.utils.fsm import AdminAddEmployee, AdminEmployee


async def set_new_privilege(callback: CallbackQuery, button: Button, manager: DialogManager):
    data = manager.middleware_data
    user_id = int(manager.dialog_data['employee_id'])
    privilege = button.widget_id
    await EmployeeHandler(data['session_maker'], data['database_logger']).update_privilege(user_id, privilege)
    await callback.answer(f'{button.text.text}')
    await manager.switch_to(AdminEmployee.info)


privilege_window = Window(
    Const('Выберите новую должность'),
    Button(Const('Менеджер'),
           id='manager',
           on_click=set_new_privilege),
    Button(Const('Модератор'),
           id='moderator',
           on_click=set_new_privilege),
    Button(Const('Куратор'),
           id='curator',
           on_click=set_new_privilege),
    Button(Const('Администратор'),
           id='admin',
           on_click=set_new_privilege,
           when='developer'),
    SwitchTo(Const("Назад"),
             state=AdminEmployee.info,
             id='bck_info'),
    state=AdminEmployee.change_privilege,
    getter=developer_getter
)
