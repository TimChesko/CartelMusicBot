from aiogram_dialog import Window, DialogManager
from aiogram_dialog.widgets.kbd import Back, Row
from aiogram_dialog.widgets.text import Format

from src.dialogs.admin.dashboard.employee.info import employee_getter
from src.dialogs.utils.buttons import BTN_BACK, TXT_CONFIRM
from src.models.employee import EmployeeHandler
from src.utils.fsm import AdminEmployee


async def delete_employee(_, __, manager: DialogManager):
    data = manager.middleware_data
    tg_id = manager.dialog_data['employee_id']
    await EmployeeHandler(data['session_maker'], data['database_logger']).update_state_to_fired(tg_id)


delete_window = Window(
    Format('Подтвердите увольнение сотрудника {name}'),
    Row(
        Back(TXT_CONFIRM, on_click=delete_employee, id="fire_employee"),
        BTN_BACK,
    ),
    state=AdminEmployee.layoff,
    getter=employee_getter
)
