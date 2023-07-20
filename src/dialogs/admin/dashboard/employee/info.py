from _operator import itemgetter

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.widgets.kbd import Start, Cancel, ScrollingGroup, Select, Group, SwitchTo, Back
from aiogram_dialog.widgets.text import Const, Format

from src.data import config
from src.models.employee import EmployeeHandler
from src.utils.fsm import AdminEmployee, AdminAddEmployee


async def employee_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    tg_id = dialog_manager.dialog_data['employee_id']
    first_name, surname, middle_name, privilege, state, add_date, fired_date, recovery_date = await EmployeeHandler(
        data['session_maker'], data['database_logger']).get_dialog_info_by_tg_id(tg_id)
    priv = {
        "admin": "Админ",
        "manager": "Менеджер",
        "moderator": "Модератор",
        "curator": "Куратор",
    }
    status = {
        'regs': "Регистрация",
        'works': "Действующий работник",
        'fired': "Уволен!"
    }
    return {
        'name': f'{first_name} {surname} {middle_name}',
        'privilege': f'{priv[privilege]}',
        'state': f'{status[state]}',
        'add_date': f'{add_date.strftime("%H:%M %Y-%m-%d") if add_date is not None else ""}',
        'fired_date': f'{fired_date.strftime("%H:%M %Y-%m-%d") if fired_date is not None else ""}',
        'recovery_date': f'{recovery_date.strftime("%H:%M %Y-%m-%d") if recovery_date is not None else ""}',
        'regs': state != 'regs',

    }


info_window = Window(
    Const('ИНФОРМАЦИЯ:\n'),
    Format('ФИО: {name}', when='regs'),
    Format('Должность: {privilege}\n'),
    Format('Статус: {state}\n'),
    Format('Дата добавления: {add_date}\n'),
    Format('Дата увольнения {fired_date}\n', when='regs'),
    Format('Дата восстановления {recovery_date}', when='regs'),
    SwitchTo(Const('Уволить'), id='delete_employee', state=AdminEmployee.on_fired),
    Back(),
    state=AdminEmployee.employee,
    getter=employee_getter
)
