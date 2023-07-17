import logging
from _operator import itemgetter

from aiogram.types import CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.widgets.kbd import Start, Cancel, ScrollingGroup, Select, Group, SwitchTo, Radio
from aiogram_dialog.widgets.text import Const, Format

from src.data import config
from src.models.employee import EmployeeHandler
from src.utils.fsm import AdminEmployee, AdminAddEmployee


async def privilege_filter(callback: CallbackQuery, btn: SwitchTo, manager: DialogManager):
    manager.start_data['filter'] = btn.widget_id
    logging.info(btn)
    if btn.widget_id in config.PRIVILEGES:
        manager.start_data['title'] = await btn.text.render_text({}, manager)
    else:
        manager.start_data['title'] = 'Сотрудники'


async def employee_getter(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.middleware_data
    privilege = dialog_manager.start_data['filter']
    title = dialog_manager.start_data['title']
    employees = await EmployeeHandler(data['engine'], data['database_logger']).get_privilege_by_filter(privilege)
    logging.info(employees)
    return {
        'privilege': employees,
        'title': title
    }


# async def on_item_selected(callback: CallbackQuery, __, manager: DialogManager, selected_item: str):
#     manager.dialog_data["employee_id"] = int(selected_item)
#     logging.info(selected_item)
#     await manager.next()


admin_main = Dialog(
    Window(
        Format("{title}"),
        Group(
            SwitchTo(Const('Админы'), id='admin', state=AdminEmployee.start, on_click=privilege_filter),
            SwitchTo(Const('Менеджеры'), id='manager', state=AdminEmployee.start, on_click=privilege_filter),
            SwitchTo(Const('Модераторы'), id='moderator', state=AdminEmployee.start, on_click=privilege_filter),
            SwitchTo(Const('Кураторы'), id='curator', state=AdminEmployee.start, on_click=privilege_filter),
            SwitchTo(Const('Сброс'), id='all', state=AdminEmployee.start, on_click=privilege_filter),
            width=3
        ),
        ScrollingGroup(
            Select(
                Format("{item[0]}"),
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
        getter=employee_getter
    )
)
