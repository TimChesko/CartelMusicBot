from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const

from src.utils.fsm import MyStudio

dialog = Dialog(
    Window(
        Const("Отгрузка"),
        state=MyStudio.public
    )
)
