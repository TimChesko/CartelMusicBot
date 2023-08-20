from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager
from aiogram_dialog.widgets.kbd import SwitchTo, Url
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.admin.common import translate_privilege
from src.dialogs.utils.buttons import BTN_BACK
from src.models.employee import EmployeeHandler
from src.utils.fsm import AdminEmployee


async def employee_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    tg_id = dialog_manager.dialog_data['employee_id']
    employee = await EmployeeHandler(data['session_maker'], data['database_logger']).get_dialog_info_by_tg_id(tg_id)
    status = {
        'regs': "Регистрация",
        'works': "Действующий работник",
        'fired': "Уволен!"
    }
    return {
        'name': employee.fullname if employee.fullname is not None else employee.tg_username,
        'privilege': translate_privilege(employee.privilege),
        'state': status[employee.state],
        'add_date': employee.add_date.strftime("%d.%m.%Y %H:%M") if employee.add_date is not None else None,
        'fired_date': employee.fired_date.strftime("%d.%m.%Y %H:%M") if employee.fired_date is not None else None,
        'recovery_date': employee.recovery_date.strftime("%d.%m.%Y %H:%M") if employee.recovery_date is not None else None,
        'username': employee.tg_username

    }


async def reinstatement_employee(callback: CallbackQuery, __, manager: DialogManager):
    data = manager.middleware_data
    tg_id = manager.dialog_data['employee_id']
    await EmployeeHandler(data['session_maker'], data['database_logger']).update_state_to_works(tg_id)
    await callback.answer('Сотрудник успешно восстановлен!')


info_window = Window(
    Const('ИНФОРМАЦИЯ:'),
    Format('Должность: {privilege}'),
    Format('ФИО: {name}'),
    Format('Статус: {state}'),
    Format('Дата добавления: {add_date}',
           when=F['add_date'].is_not(None)),
    Format('Дата увольнения: {fired_date}',
           when=F['fired_date'].is_not(None)),
    Format('Дата восстановления: {recovery_date}',
           when=F['recovery_date'].is_not(None)),
    Url(Const('Написать'),
        Format('https://t.me/{username}'),
        when=F['username'].is_not(None)),
    SwitchTo(Const('Восстановить'),
             id='reinstatement_employee',
             state=AdminEmployee.info,
             on_click=reinstatement_employee,
             when='fired'),
    SwitchTo(Const('Изменить должность'),
             id='change_privilege',
             state=AdminEmployee.change_privilege,
             when='not_fired'),
    SwitchTo(Const('Уволить'),
             id='delete_employee',
             state=AdminEmployee.layoff,
             when='not_fired'),
    BTN_BACK,
    state=AdminEmployee.info,
    getter=employee_getter
)
