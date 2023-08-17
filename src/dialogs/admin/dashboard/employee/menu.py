import logging
from _operator import itemgetter

from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.widgets.kbd import Start, ScrollingGroup, Select, Group, SwitchTo
from aiogram_dialog.widgets.text import Const, Format, Case

from src.dialogs.admin.dashboard.employee.delete import delete_window
from src.dialogs.admin.dashboard.employee.info import info_window
from src.dialogs.admin.dashboard.employee.privilege import privilege_window
from src.dialogs.utils.buttons import BTN_CANCEL_BACK
from src.models.employee import EmployeeHandler
from src.utils.fsm import AdminEmployee, AdminAddEmployee


async def on_start(_, dialog_manager: DialogManager):
    dialog_manager.dialog_data['filter'] = dialog_manager.start_data['filter']
    dialog_manager.dialog_data['title'] = dialog_manager.start_data['title']


async def privilege_filter(_, btn: SwitchTo, manager: DialogManager):
    manager.dialog_data['filter'] = btn.widget_id


async def employee_list_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    config = data['config']
    dialog_data = dialog_manager.dialog_data
    privilege = dialog_data['filter']
    employees = await (EmployeeHandler(data['session_maker'], data['database_logger']).
                       get_privilege_by_filter(config, privilege))
    buttons = {
        "admin": "Админ",
        "manager": "Менеджер",
        "moderator": "Модератор",
        "curator": "Куратор",
        "regs": "Нереги",
        "fired": "Уволены"
    }
    if "filter" in dialog_data and dialog_data["filter"] in buttons:
        text = buttons[dialog_data["filter"]]
        buttons[dialog_data["filter"]] = f"🔘 {text}"
    return {
        'privilege': employees,
        'developer': dialog_manager.event.from_user.id in config.constant.developers,
        'is_fullname': employees is not None,
        **buttons
    }


async def on_item_selected(_, __, manager: DialogManager, selected_item: str):
    manager.dialog_data["employee_id"] = int(selected_item)
    await manager.next()


# noinspection PyTypeChecker
employees = Dialog(
    Window(
        Const("Сотрудники"),
        Group(
            SwitchTo(Format('{admin}'), id='ADMIN', state=AdminEmployee.start, on_click=privilege_filter),
            SwitchTo(Format('{manager}'), id='MANAGER', state=AdminEmployee.start, on_click=privilege_filter),
            SwitchTo(Format('{moderator}'), id='MODERATOR', state=AdminEmployee.start, on_click=privilege_filter),
            SwitchTo(Format('{curator}'), id='CURATOR', state=AdminEmployee.start, on_click=privilege_filter),
            SwitchTo(Format('{regs}'), id='regs', state=AdminEmployee.start, on_click=privilege_filter),
            SwitchTo(Const('Сброс'), id='all', state=AdminEmployee.start, on_click=privilege_filter),
            SwitchTo(Format('🔻{fired}🔻'), id='fired', state=AdminEmployee.start, on_click=privilege_filter,
                     when="developer"),
            width=3
        ),
        ScrollingGroup(
            Select(
                Format('{item.tg_username}'),
                id="ms",
                items="privilege",
                item_id_getter=lambda emp: emp.tg_id,
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
            BTN_CANCEL_BACK,
            width=2
        ),
        state=AdminEmployee.start,
        getter=employee_list_getter
    ),
    info_window,
    delete_window,
    privilege_window,
    on_start=on_start
)
