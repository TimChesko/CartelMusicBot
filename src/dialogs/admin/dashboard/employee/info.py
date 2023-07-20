from aiogram.types import CallbackQuery
from aiogram_dialog import Window, DialogManager
from aiogram_dialog.widgets.kbd import SwitchTo, Back, Button, Url
from aiogram_dialog.widgets.text import Const, Format

from src.models.employee import EmployeeHandler
from src.utils.fsm import AdminEmployee


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
        'name': f'{surname} {first_name} {middle_name}' \
            if first_name or surname or middle_name is not None else f'@{dialog_manager.dialog_data["username"]}',
        'privilege': f'{priv[privilege]}',
        'state': f'{status[state]}',
        'add_date': f'{add_date.strftime("%d.%m.%Y %H:%M") if add_date is not None else ""}',
        'fired_date': f'{fired_date.strftime("%d.%m.%Y %H:%M") if fired_date is not None else ""}',
        'recovery_date': f'{recovery_date.strftime("%d.%m.%Y %H:%M") if recovery_date is not None else ""}',
        'regs': state != 'regs',
        'fired': state == 'fired',
        'not_fired': state != 'fired',
        'username': dialog_manager.dialog_data["username"]

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
    Format('Дата добавления: {add_date}'),
    Format('Дата увольнения: {fired_date}',
           when='regs'),
    Format('Дата восстановления: {recovery_date}',
           when='regs'),
    Url(Const('Написать'),
        Format('https://t.me/{username}')),
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
    Back(Const("Назад")),
    state=AdminEmployee.info,
    getter=employee_getter
)
