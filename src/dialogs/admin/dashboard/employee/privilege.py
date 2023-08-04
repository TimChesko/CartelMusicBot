from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Const

from src.dialogs.admin.dashboard.employee.add import developer_getter
from src.dialogs.utils.buttons import TXT_BACK
from src.models.employee import EmployeeHandler
from src.utils.fsm import AdminEmployee


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
    SwitchTo(Const(TXT_BACK),
             state=AdminEmployee.info,
             id='bck_info'),
    state=AdminEmployee.change_privilege,
    getter=developer_getter
)
