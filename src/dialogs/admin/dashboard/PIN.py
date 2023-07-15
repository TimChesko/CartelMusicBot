import logging

from aiogram_dialog import Window, Dialog, LaunchMode, DialogManager
from aiogram_dialog.widgets.kbd import Start, Cancel
from aiogram_dialog.widgets.text import Const

from src.dialogs.utils.common import on_start_copy_start_data
from src.models.user import UserHandler
from src.utils.fsm import AdminMenu, AdminListening, AdminDashboardPIN, AdminDashboard

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
