from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import SwitchTo, Button
from aiogram_dialog.widgets.text import Const

from src.dialogs.utils.buttons import BTN_BACK, BTN_CANCEL_BACK, coming_soon
from src.utils.fsm import ViewStatus, MyStudio


async def view_status(callback: CallbackQuery, button: Button, manager: DialogManager):
    data = {"status": callback.data.split("_")[-1], "status_text": button.text.text.lower()}
    await manager.start(state=ViewStatus.menu, data=data)


dialog = Dialog(
    Window(
        Const("🎙 Моя студия"),
        SwitchTo(Const("🎧 Список треков"), id="studio_my_tracks", state=MyStudio.my_tracks),
        Button(Const("💿 Список релизов"), id="studio_status_public", on_click=coming_soon),
        BTN_CANCEL_BACK,
        state=MyStudio.menu
    ),
    Window(
        Const("❇️ Статус треков"),
        Button(Const("✅ Приняты"), id="studio_status_approve", on_click=view_status),
        Button(Const("🕑 На проверке"), id="studio_status_process", on_click=view_status),
        Button(Const("⛔️ Отклонены"), id="studio_status_reject", on_click=view_status),
        BTN_BACK,
        state=MyStudio.my_tracks
    )
)
