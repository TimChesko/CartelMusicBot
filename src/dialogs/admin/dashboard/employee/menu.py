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
from src.utils.enums import Privileges, EmployeeStatus
from src.utils.fsm import AdminEmployee, AdminAddEmployee


# async def privilege_filter(_, btn: SwitchTo, manager: DialogManager):
#     manager.dialog_data['filter'] = btn.widget_id


async def employee_list_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    # config = data['config']
    employees = await (EmployeeHandler(data['session_maker'], data['database_logger']).
                       get_privilege_by_filter())
    # buttons = {
    #     f"{Privileges.ADMIN}": "Админ",
    #     f"{Privileges.MANAGER}": "Менеджер",
    #     f"{Privileges.MODERATOR}": "Модератор",
    #     f"{Privileges.CURATOR}": "Куратор",
    #     f"{EmployeeStatus.REGISTRATION}": "Нереги",
    #     f"{EmployeeStatus.FIRED}": "Уволены"
    # }
    # if "filter" in dialog_data and dialog_data["filter"] in buttons:
    #     text = buttons[dialog_data["filter"]]
    #     buttons[dialog_data["filter"]] = f"🔘 {text}"
    return {
        'privilege': employees,
        # 'developer': dialog_manager.event.from_user.id in config.constant.developers,
        # **buttons
    }


async def on_item_selected(_, __, manager: DialogManager, selected_item: str):
    manager.dialog_data["employee_id"] = int(selected_item)
    await manager.next()


# noinspection PyTypeChecker
employees = Dialog(
    Window(
        Const("Сотрудники"),
        # Group(
        #     SwitchTo(Format('f{admin}'), id='ADMIN', state=AdminEmployee.start, on_click=privilege_filter),
        #     SwitchTo(Format('f{manager}'), id='MANAGER', state=AdminEmployee.start, on_click=privilege_filter),
        #     SwitchTo(Format('f{moderator}'), id='MODERATOR', state=AdminEmployee.start, on_click=privilege_filter),
        #     SwitchTo(Format('f{curator}'), id='CURATOR', state=AdminEmployee.start, on_click=privilege_filter),
        #     SwitchTo(Format('f{regs}'), id='regs', state=AdminEmployee.start, on_click=privilege_filter),
        #     SwitchTo(Const('Сброс'), id='all', state=AdminEmployee.start, on_click=privilege_filter),
        #     SwitchTo(Format('🔻{fired}🔻'), id='fired', state=AdminEmployee.start, on_click=privilege_filter,
        #              when="developer"),
        #     width=3
        # ),
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
            width=1
        ),
        state=AdminEmployee.start,
        getter=employee_list_getter
    ),
    info_window,
    delete_window,
    privilege_window
)
