from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from src.dialogs.utils.buttons import BTN_CANCEL_BACK
from src.utils.fsm import AdminDashboard, AdminStatistic, AdminEmployee, AdminTemplates

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
        Start(Const('Шаблоны'),
              id='admin_templates',
              state=AdminTemplates.start),
        BTN_CANCEL_BACK,
        state=AdminDashboard.start
    ),
)
