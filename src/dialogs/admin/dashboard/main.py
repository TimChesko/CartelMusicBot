from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import Start, Cancel
from aiogram_dialog.widgets.text import Const

from src.data import config
from src.dialogs.utils.common import on_start_copy_start_data
from src.models.user import UserHandler
from src.utils.fsm import AdminMenu, AdminListening, AdminDashboardPIN, AdminDashboard, AdminAddEmployee, AdminStatistic

dashboard = Dialog(
    Window(
        Const('АДМИН ПАНЕЛЬ'),
        Start(Const('Добавить работника'),
              id='add_employee',
              state=AdminAddEmployee.start),
        Start(Const('Статистика'),
              id='admin_stats',
              state=AdminStatistic.start),
        Cancel(),
        state=AdminDashboard.start
    ),
)
