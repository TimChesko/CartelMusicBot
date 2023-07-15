from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Window, Dialog, LaunchMode, DialogManager
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Start, Cancel, Button, Row, Back
from aiogram_dialog.widgets.text import Const, Format

from src.data import config
from src.dialogs.utils.common import on_start_copy_start_data
from src.models.user import UserHandler
from src.utils.fsm import AdminMenu, AdminListening, AdminDashboardPIN, AdminDashboard, AdminEmployee, AdminAddEmployee

