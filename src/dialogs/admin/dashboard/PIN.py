from aiogram_dialog import Window, Dialog
from aiogram_dialog.widgets.kbd import Start, Cancel
from aiogram_dialog.widgets.text import Const

from src.utils.fsm import AdminDashboardPIN, AdminDashboard

code = Dialog(
    Window(
        Const('Введите пин код'),
        Start(Const('Next'),
              id='pin_code',
              state=AdminDashboard.start),
        Cancel(),
        state=AdminDashboardPIN.start
    )
)
