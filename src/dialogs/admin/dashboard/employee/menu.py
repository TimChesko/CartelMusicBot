from aiogram_dialog import Window, Dialog, LaunchMode, DialogManager
from aiogram_dialog.widgets.kbd import Start, Cancel
from aiogram_dialog.widgets.text import Const

from src.dialogs.utils.common import on_start_copy_start_data
from src.models.user import UserHandler
from src.utils.fsm import AdminMenu, AdminListening, AdminDashboardPIN, AdminDashboard, AdminEmployee, AdminAddEmployee

admin_main = Dialog(
    Window(

        Const('СОТРУДНИКИ'),
        Start(Const('Добавить'),
              id='employee_add',
              state=AdminAddEmployee.start),
        # Start(Const('Статистика')),
        # Start(Const('Настройки')),
        state=AdminEmployee.start
    )
)