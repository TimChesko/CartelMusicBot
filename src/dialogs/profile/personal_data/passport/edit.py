from operator import itemgetter

from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Cancel
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.profile import personal_data
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


async def create_list_buttons(list_edit: list) -> list:
    passport = personal_data.string.passport
    result = []
    for item in list_edit:
        if item in passport:
            info = passport[item]
            result.append([item, info['type']])
    return result


async def profile_edit_getter(dialog_manager: DialogManager, **_kwargs):
    data = dialog_manager.middleware_data
    user_id = data['event_from_user'].id
    list_edit = await get_list_edit(data, dialog_manager, user_id)
    if len(list_edit) == 0:
        await dialog_manager.done()
    return {
        "profile_edit": await create_list_buttons(list_edit)
    }


async def get_list_edit(data, dialog_manager, user_id):
    if dialog_manager.start_data['type_data'] == "passport":
        list_edit = await PersonalDataHandler(data['engine'], data['database_logger']).find_none_columns_passport(
            user_id)
    elif dialog_manager.start_data['type_data'] == "bank":
        list_edit = await PersonalDataHandler(data['engine'], data['database_logger']).find_none_columns_bank(user_id)
    else:
        list_edit = []
    return list_edit


async def on_click_edit(_, __, manager: DialogManager, data):
    middleware_data = manager.middleware_data
    user_id = middleware_data['event_from_user'].id
    list_edit = await get_list_edit(middleware_data, manager, user_id)
    await manager.start(data={"profile_edit": data, "count_edit": len(list_edit)})


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
    Window(
        Format("{request}"),
        Cancel(Const("Отменить процедуру")),
        state=ProfileEdit.process
    )
)
