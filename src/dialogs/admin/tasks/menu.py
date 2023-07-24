from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from src.dialogs.utils.buttons import BTN_CANCEL_BACK
from src.utils.fsm import AdminViewTypeDocs, AdminCheckPassport

dialog = Dialog(
    Window(
        Const("Выберете категорию для проверки"),
        Start(Const("Паспортные данные"), id="check_passport", state=AdminCheckPassport.menu),
        # Start(Const("Банковсие данные"), id="check_bank", state=...),
        # Start(Const("Документы к треку"), id="check_track_info", state=...),
        BTN_CANCEL_BACK,
        state=AdminViewTypeDocs.menu
    )
)
