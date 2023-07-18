import logging
from _operator import itemgetter

from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.widgets.kbd import Start, Cancel, ScrollingGroup, Select, Group, SwitchTo, Back
from aiogram_dialog.widgets.text import Const, Format

from src.models.employee import EmployeeHandler
from src.utils.fsm import AdminEmployee, AdminAddEmployee


async def on_start(_, dialog_manager: DialogManager):
    dialog_manager.dialog_data['filter'] = dialog_manager.start_data['filter']
    dialog_manager.dialog_data['title'] = dialog_manager.start_data['title']


async def privilege_filter(_, btn: SwitchTo, manager: DialogManager):
    manager.dialog_data['filter'] = btn.widget_id


async def employee_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    tg_id = dialog_manager.dialog_data['employee_id']
    logging.info(await EmployeeHandler(
        data['session_maker'], data['database_logger']).get_dialog_info_by_tg_id(tg_id))
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


async def employee_list_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    dialog_data = dialog_manager.dialog_data
    privilege = dialog_data['filter']
    # TODO Также добавить отдельный список для всех нереганных
    employees = await EmployeeHandler(data['session_maker'], data['database_logger']).get_privilege_by_filter(privilege)
    logging.info(employees)
    buttons = {
        "admin": "Админ",
        "manager": "Менеджер",
        "moderator": "Модератор",
        "curator": "Куратор",
    }
    if "filter" in dialog_data and dialog_data["filter"] in buttons:
        text = buttons[dialog_data["filter"]]
        buttons[dialog_data["filter"]] = f"🔘 {text}"
    return {
        'privilege': [(tg_id, firstname if firstname else tg_username, surname if surname else '') for
                      tg_id, tg_username, firstname, surname in employees],
        **buttons
    }


async def on_item_selected(_, __, manager: DialogManager, selected_item: str):
    manager.dialog_data["employee_id"] = int(selected_item)
    await manager.next()


admin_main = Dialog(
    Window(
        Const("Сотрудники"),
        Group(
            SwitchTo(Format('{admin}'), id='admin', state=AdminEmployee.start, on_click=privilege_filter),
            SwitchTo(Format('{manager}'), id='manager', state=AdminEmployee.start, on_click=privilege_filter),
            SwitchTo(Format('{moderator}'), id='moderator', state=AdminEmployee.start, on_click=privilege_filter),
            SwitchTo(Format('{curator}'), id='curator', state=AdminEmployee.start, on_click=privilege_filter),
            SwitchTo(Const('Сброс'), id='all', state=AdminEmployee.start, on_click=privilege_filter),
            width=3
        ),
        ScrollingGroup(
            Select(
                Format("{item[2]} {item[1]}"),
                id="ms",
                items="privilege",
                item_id_getter=itemgetter(0),
                on_click=on_item_selected
            ),
            width=1,
            height=5,
            id='scroll_tracks_with_pager',
        ),
        Group(
            Start(Const('Добавить'),
                  id='employee_add',
                  state=AdminAddEmployee.start),
            Cancel(),
            width=2
        ),
        state=AdminEmployee.start,
        getter=employee_list_getter
    ),
    Window(
        Format('ИНФОРМАЦИЯ:\n'
               'ФИО: {name}', when='regs'),
        Format('Должность: {privilege}\n'),
        Format('Статус: {state}\n'),
        Format('Дата добавления: {add_date}\n'),
        Format('Дата увольнения {fired_date}\n', when='regs'),
        Format('Дата восстановления {recovery_date}', when='regs'),
        SwitchTo(Const('Уволить'), id='delete_employee', state=AdminEmployee.on_fired),
        Back(),
        state=AdminEmployee.employee,
        getter=employee_getter
    ),
    on_start=on_start
)
