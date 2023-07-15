import logging
from operator import itemgetter
from typing import Any

from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Cancel
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.profile.personal_data import string
from src.dialogs.profile.personal_data.process.input_factory import start_dialog_filling_profile
from src.dialogs.profile.personal_data.process.process import process_input
from src.models.personal_data import PersonalDataHandler
from src.utils.fsm import ProfileEdit


async def update_edit_data(location, data, middleware_data, start_data, user_id):
    """
    :param location: passport or bank
    :param data: new value
    :param middleware_data:
    :param start_data:
    :param user_id:
    :return: None
    """
    await PersonalDataHandler(middleware_data['engine'], middleware_data['database_logger']). \
        update_personal_data(user_id, start_data['profile_edit'], data, location, start_data['count_edit'])


async def create_list_buttons(manager: DialogManager, list_edit: list) -> list:
    data = string.personal_data[manager.start_data['type_data']]
    result = []
    for item in list_edit:
        if item in data:
            info = data[item]
            result.append([item, info['type']])
    return result


async def profile_edit_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    user_id = data['event_from_user'].id
    list_edit = await get_list_edit(data, dialog_manager, user_id)
    return {
        "profile_edit": await create_list_buttons(dialog_manager, list_edit)
    }


async def get_list_edit(data, manager, user_id):
    if manager.dialog_data['type_data'] == "passport":
        list_edit = await PersonalDataHandler(data['engine'], data['database_logger']).find_none_columns_passport(
            user_id)
    elif manager.dialog_data['type_data'] == "bank":
        list_edit = await PersonalDataHandler(data['engine'], data['database_logger']).find_none_columns_bank(user_id)
    else:
        list_edit = []
    return list_edit


async def on_click_edit(_, __, manager: DialogManager, data):
    await start_dialog_filling_profile(manager.dialog_data['type_data'], data, manager)


async def process_result(_, result: Any, manager: DialogManager):
    personal_data_type = manager.dialog_data['type_data']
    manager.dialog_data['data_name'] = result[1]
    manager.dialog_data['count_edit'] = \
        len(await get_list_edit(manager.middleware_data, manager, manager.middleware_data['event_from_user'].id))
    if "back" != result[0]:
        next_turn = await process_input(True, result,
                                        string.personal_data[personal_data_type][result[1]]['input'],
                                        manager)
        if not next_turn:
            return
    manager.dialog_data['count_edit'] = \
        len(await get_list_edit(manager.middleware_data, manager, manager.middleware_data['event_from_user'].id))
    if manager.dialog_data['count_edit'] == 0:
        await manager.done()


async def on_start(_, manager: DialogManager):
    manager.dialog_data['type_data'] = manager.start_data['type_data']


dialog = Dialog(
    Window(
        Const("Выберете что вы хотите изменить"),
        ScrollingGroup(
            Select(
                Format("{item[1]}"),
                id="scroll_profile",
                items="profile_edit",
                item_id_getter=itemgetter(0),
                on_click=on_click_edit
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
    on_process_result=process_result,
    on_start=on_start
)
