from operator import itemgetter

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window, ShowMode
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Cancel, Button, Back
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.utils.widgets.input_forms.process_input import process_input_result, InputForm
from src.dialogs.utils.widgets.input_forms.utils import convert_database_to_data
from src.models.personal_data import PersonalDataHandler
from src.utils.fsm import ProfileEdit


async def get_list_edit(manager: DialogManager) -> dict:
    middleware_data = manager.middleware_data
    user_id = middleware_data['event_from_user'].id
    data = await PersonalDataHandler(middleware_data['engine'], middleware_data['database_logger']). \
        get_personal_data_by_header(user_id, manager.dialog_data['header_data'])
    return await convert_database_to_data(data)


async def create_list_buttons(list_edit: dict) -> list:
    result = []
    for item in list_edit:
        result.append([list_edit[item]['data_name'], list_edit[item]['title']])
    return result


async def profile_edit_getter(dialog_manager: DialogManager, **_kwargs):
    list_edit = await get_list_edit(dialog_manager)
    return {
        "profile_edit": await create_list_buttons(list_edit)
    }


async def create_form(_, __, manager: DialogManager, *_kwargs):
    buttons = [False, True, False]
    task_list = await get_list_edit(manager)
    await InputForm(manager).start_dialog(buttons, task_list)


async def on_finally(callback: CallbackQuery, __, manager: DialogManager):
    middleware_data = manager.middleware_data
    user_id = middleware_data['event_from_user'].id
    await PersonalDataHandler(middleware_data['engine'], middleware_data['database_logger']). \
        update_personal_data(user_id, manager.dialog_data['header_data'], manager.dialog_data['save_input'])
    await callback.message.answer("Вы успешно изменили данные !")
    manager.show_mode = ShowMode.SEND
    info = await get_list_edit(manager)
    if info is None or info == {}:
        await manager.done()
    else:
        await manager.switch_to(state=ProfileEdit.menu)


async def on_start(_, manager: DialogManager):
    manager.dialog_data['header_data'] = manager.start_data['header_data']


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
        Cancel(Const("< Вернуться в профиль")),
        getter=profile_edit_getter,
        state=ProfileEdit.menu,
    ),
    Window(
        Const("Проверьте и подтвердите правильность всех данных."
              "В целях безопасности, в дальнейшем у вас не будет возможности просмотреть"
              " внесенные данные без помощи модераторов."),
        Button(Const("Подтвердить"), id="edit_confirm", on_click=on_finally),
        Back(Const("Назад")),
        state=ProfileEdit.confirm
    ),
    on_process_result=process_input_result,
    on_start=on_start
)
