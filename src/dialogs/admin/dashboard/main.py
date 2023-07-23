from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Start, Cancel
from aiogram_dialog.widgets.text import Const

from src.utils.fsm import AdminDashboard, AdminStatistic, AdminEmployee

dashboard = Dialog(
    Window(
        Const('АДМИН ПАНЕЛЬ'),
        Start(Const('Сотрудники'),
              id='add_employee',
              state=AdminEmployee.start,
              data={'filter': '',
                    'title': 'Сотрудники'}),
        Start(Const('Статистика'),
              id='admin_stats',
              state=AdminStatistic.start),
        Cancel(Const('Главное меню')),
        state=AdminDashboard.start
    ),
)
