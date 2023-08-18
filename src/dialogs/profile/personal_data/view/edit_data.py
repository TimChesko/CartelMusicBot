from operator import itemgetter

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window, ShowMode
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Button, Row
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.utils.buttons import TXT_CONFIRM, BTN_BACK, BTN_CANCEL_BACK
from src.dialogs.utils.common import on_start_copy_start_data
from src.dialogs.utils.widgets.input_forms.process_input import process_input_result, InputForm
from src.dialogs.utils.widgets.input_forms.utils import convert_database_to_data, convert_data_types, get_key_value
from src.models.personal_data import PersonalDataHandler
from src.utils.fsm import ProfileEdit


class DialogManagerOptimized:
    def __init__(self, session_maker, database_logger):
        self.personal_data_handler = PersonalDataHandler(session_maker, database_logger)

    async def get_personal_data(self, user_id, header_data):
        return await self.personal_data_handler.get_personal_data_by_header(user_id, header_data)

    async def update_personal_data(self, user_id, header_data, save_input):
        return await self.personal_data_handler.update_personal_data(user_id, header_data, save_input)


async def get_data_list(manager: DialogManager) -> dict:
    user_id = manager.event.from_user.id
    dm_optimized = DialogManagerOptimized(
        manager.middleware_data['session_maker'],
        manager.middleware_data['database_logger']
    )
    data = await dm_optimized.get_personal_data(user_id, manager.dialog_data['header_data'])
    return await convert_database_to_data(data)


async def create_button_list(data_list: dict) -> list:
    return [[item_data['data_name'], item_data['title']] for item_data in data_list.values()]


async def profile_edit_getter(dialog_manager: DialogManager, **_kwargs):
    data_list = await get_data_list(dialog_manager)
    return {
        "profile_edit": await create_button_list(data_list)
    }


async def create_form(callback: CallbackQuery, _, manager: DialogManager, *_kwargs):
    buttons = [False, True, True]
    data_list = await get_data_list(manager)
    key = callback.data.split(":")[-1]
    task = {key: data_list[key]}
    await InputForm(manager).start_dialog(buttons, task)


async def on_finally(callback: CallbackQuery, __, manager: DialogManager):
    user_id = manager.event.from_user.id
    support = manager.middleware_data['config'].constant.support
    dm_optimized = DialogManagerOptimized(
        manager.middleware_data['session_maker'],
        manager.middleware_data['database_logger']
    )
    data_values = await get_key_value(manager.dialog_data['save_input'])
    data = await convert_data_types(data_values)
    answer = await dm_optimized.update_personal_data(user_id, manager.dialog_data['header_data'], data)
    if answer:
        text = "✅ Вы успешно изменили данные !"
    else:
        text = f'❌ Произошел сбой на стороне сервера. Обратитесь в поддержку {support}'
    await callback.message.edit_text(text)
    manager.show_mode = ShowMode.SEND
    if not await get_data_list(manager):
        await manager.done()
    else:
        await manager.switch_to(state=ProfileEdit.menu)


dialog = Dialog(
    Window(
        Const("Выберете что вы хотите изменить"),
        ScrollingGroup(
            Select(
                Format("{item[1]}"),
                id="scroll_profile",
                items="profile_edit",
                item_id_getter=itemgetter(0),
                on_click=create_form
            ),
            width=1,
            height=5,
            hide_on_single_page=True,
            id='scroll_profile_data_edit',
        ),
        BTN_CANCEL_BACK,
        getter=profile_edit_getter,
        state=ProfileEdit.menu,
    ),
    Window(
        Const("🔰 Проверьте и подтвердите правильность всех данных"),
        Row(
            BTN_BACK,
            Button(TXT_CONFIRM, id="edit_confirm", on_click=on_finally),
        ),
        state=ProfileEdit.confirm
    ),
    on_process_result=process_input_result,
    on_start=on_start_copy_start_data
)
