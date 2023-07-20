from _operator import itemgetter

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.widgets.kbd import Start, Cancel, ScrollingGroup, Select, Group, SwitchTo, Back
from aiogram_dialog.widgets.text import Const, Format

from src.data import config
from src.dialogs.admin.dashboard.employee.info import info_window
from src.models.employee import EmployeeHandler
from src.utils.fsm import AdminEmployee, AdminAddEmployee


async def on_start(_, dialog_manager: DialogManager):
    dialog_manager.dialog_data['filter'] = dialog_manager.start_data['filter']
    dialog_manager.dialog_data['title'] = dialog_manager.start_data['title']


async def privilege_filter(_, btn: SwitchTo, manager: DialogManager):
    manager.dialog_data['filter'] = btn.widget_id


async def employee_list_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    dialog_data = dialog_manager.dialog_data
    privilege = dialog_data['filter']
    employees = await EmployeeHandler(data['session_maker'], data['database_logger']).get_privilege_by_filter(privilege)
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
        'privilege': [(tg_id, firstname if firstname else tg_username, surname if surname else '') for
                      tg_id, tg_username, firstname, surname in employees],
        'developer': data['event_from_user'].id in config.DEVELOPERS,
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
            SwitchTo(Format('{regs}'), id='regs', state=AdminEmployee.start, on_click=privilege_filter),
            SwitchTo(Const('Сброс'), id='all', state=AdminEmployee.start, on_click=privilege_filter),
            SwitchTo(Format('{fired}'), id='fired', state=AdminEmployee.start, on_click=privilege_filter,
                     when="developer"),
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
    info_window,
    on_start=on_start
)
