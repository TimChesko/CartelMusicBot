from aiogram.types import CallbackQuery
from aiogram_dialog import Window, Dialog, DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from src.models.personal_data import PersonalDataHandler
from src.utils.fsm import PersonalData, Profile


async def update_data(callback: CallbackQuery, _, manager: DialogManager):
    data = manager.middleware_data
    user_id = data['event_from_user'].id
    await PersonalDataHandler(data['engine'], data['database_logger']).confirm_personal_data(user_id)
    await manager.start(state=Profile.menu)
    await manager.done()

confirm_personal_data = Dialog(
    Window(
        # TODO добавить картинку
        Const("Нажимая кнопку ниже, я даю согласие на обработку персональных данных и принимаю условия оферты."),
        Button(Const("Принять"), id="confirm_personal_data", on_click=update_data),
        state=PersonalData.confirm
    )
)
