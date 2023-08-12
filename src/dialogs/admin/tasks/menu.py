from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from src.dialogs.utils.buttons import BTN_CANCEL_BACK
from src.utils.fsm import AdminViewTypeDocs, AdminCheckPassport, AdminListTracks, AdminRelease

dialog = Dialog(
    Window(
        Const("Выберете категорию для проверки"),
        Start(Const("🪪 Верификация"), id="check_passport", state=AdminCheckPassport.menu),
        Start(Const("🎶 Инфо по треку"), id="check_track_info", state=AdminListTracks.menu),
        Start(Const("🧾 Лицензионка"), id="check_release_info", state=AdminRelease.menu),
        BTN_CANCEL_BACK,
        state=AdminViewTypeDocs.menu
    )
)
