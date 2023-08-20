from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.utils.buttons import TXT_NEXT, BTN_CANCEL_BACK, TXT_APPROVE, TXT_BACK
from src.dialogs.utils.widgets.input_forms.process_input import process_input_result, InputForm
from src.dialogs.utils.widgets.input_forms.utils import convert_data_types, get_data_from_db, get_key_value
from src.dialogs.utils.widgets.input_forms.window_input import start_dialog_filling_profile
from src.models.personal_data import PersonalDataHandler
from src.utils.fsm import Bank


async def create_form(_, __, manager: DialogManager):
    buttons = [False, True, True]
    task_list = await get_data_from_db("bank", manager)
    await InputForm(manager).start_dialog(buttons, task_list)


async def on_finally_bank(callback: CallbackQuery, _, manager: DialogManager):
    middleware_data = manager.middleware_data
    support = middleware_data['config'].constant.support
    user_id = manager.event.from_user.id
    data_values = await get_key_value(manager.dialog_data['save_input'])
    data = await convert_data_types(data_values)
    answer = await PersonalDataHandler(middleware_data['session_maker'], middleware_data['database_logger']). \
        update_all_personal_data(user_id, "bank", data)
    if answer:
        text = "✅ Вы успешно внесли банковские данные !"
    else:
        text = f'❌ Произошел сбой на стороне сервера. Обратитесь в поддержку {support}'
    await callback.message.delete()
    await middleware_data["bot"].send_message(chat_id=user_id, text=text)
    manager.show_mode = ShowMode.SEND
    await manager.done()


async def back_dialog(_, __, manager: DialogManager):
    task_list_done = manager.dialog_data["task_list_done"]
    task_list_process = manager.dialog_data["task_list_process"]
    manager.current_context().state = Bank.add_data
    if len(task_list_done) != 0:
        task_list_process.insert(0, task_list_done.pop())
        await start_dialog_filling_profile(*(await InputForm(manager).get_args()))
    else:
        await manager.done()


async def get_finish_data(dialog_manager: DialogManager, **_kwargs):
    text = ""
    for column, items in dialog_manager.dialog_data['save_input'].items():
        text += f"{items['title']}: <b>{items['value']}</b>\n"
    return {
        "text": text,
    }


add_full_data = Dialog(
    Window(
        Const("❇️ Перед началом заполнения данных, пожалуйста, прочитайте данную статью о "
              "том что нужно подготовить - "
              '<a href="https://telegra.ph/Bankovskie-dannye-08-14">СТАТЬЯ</a>'),
        Button(
            TXT_NEXT,
            id="bank_start",
            on_click=create_form
        ),
        BTN_CANCEL_BACK,
        state=Bank.add_data,
        disable_web_page_preview=True
    ),
    Window(
        Format("{text}"),
        Const("🔰 Проверьте и подтвердите правильность всех данных.\n"),
        Const("🔒 В целях безопасности, в дальнейшем у вас не будет возможности изменить или просмотреть"
              " внесенные данные без помощи модераторов."),
        Row(
            Button(TXT_BACK, id="bank_back", on_click=back_dialog),
            Button(TXT_APPROVE, id="bank_confirm", on_click=on_finally_bank),
        ),
        getter=get_finish_data,
        state=Bank.confirm
    ),
    on_process_result=process_input_result,
)
