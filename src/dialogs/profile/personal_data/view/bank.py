from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets.kbd import Button, Cancel
from aiogram_dialog.widgets.text import Const

from src.dialogs.utils.buttons import TXT_CONFIRM, BTN_BACK
from src.dialogs.utils.widgets.input_forms.process_input import process_input_result, InputForm
from src.dialogs.utils.widgets.input_forms.utils import convert_data_types, get_data_from_db
from src.models.personal_data import PersonalDataHandler
from src.utils.fsm import Bank


async def create_form(_, __, manager: DialogManager):
    buttons = [False, True, True]
    task_list = await get_data_from_db("bank", manager)
    await InputForm(manager).start_dialog(buttons, task_list)


async def on_finally_bank(callback: CallbackQuery, _, manager: DialogManager):
    middleware_data = manager.middleware_data
    user_id = manager.event.from_user.id
    data = await convert_data_types(manager.dialog_data['save_input'])

    await PersonalDataHandler(middleware_data['session_maker'], middleware_data['database_logger']). \
        update_all_personal_data(user_id, "bank", data)

    await callback.message.answer("Вы успешно внесли данные о банке !\n"
                                  "Чтобы обезопасить себя, нажмите на 3 точки в правом углу, "
                                  "затем clear history/очистить историю. Чтобы удалить все внесенные данные из чата.")
    manager.show_mode = ShowMode.SEND
    await manager.done()


add_full_data = Dialog(
    Window(
        Const("Перед началом заполнения данных, подготовьте банковские данные."),
        Button(
            Const("Продолжить"),
            id="bank_start",
            on_click=create_form
        ),
        Cancel(Const("Вернуться в профиль")),
        state=Bank.add_data
    ),
    Window(
        Const("Проверьте и подтвердите правильность всех данных."
              "В целях безопасности, в дальнейшем у вас не будет возможности просмотреть"
              " внесенные данные без помощи модераторов."),
        Button(TXT_CONFIRM, id="bank_confirm", on_click=on_finally_bank),
        BTN_BACK,
        state=Bank.confirm
    ),
    on_process_result=process_input_result,
)
