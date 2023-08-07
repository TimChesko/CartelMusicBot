from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from src.dialogs.utils.buttons import BTN_CANCEL_BACK
from src.utils.fsm import AdminViewTypeDocs, AdminCheckPassport, AdminListTracks

dialog = Dialog(
    Window(
        Const("Выберете категорию для проверки"),
        Start(Const("Конфиденциальные данные"), id="check_passport", state=AdminCheckPassport.menu),
        Start(Const("Документы к треку"), id="check_track_info", state=AdminListTracks.menu),
        BTN_CANCEL_BACK,
        state=AdminViewTypeDocs.menu
    )
)
