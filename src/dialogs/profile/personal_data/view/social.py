from operator import itemgetter

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Cancel, Button, Row, Back, Url, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.utils.widgets.input_forms.process_input import process_input_result, InputForm
from src.dialogs.utils.widgets.input_forms.utils import get_data_from_db
from src.models.personal_data import PersonalDataHandler
from src.utils.fsm import Social


async def get_data(dialog_manager: DialogManager, **_kwargs):
    middle = dialog_manager.middleware_data
    user_id = middle['event_from_user'].id
    list = await PersonalDataHandler(middle['engine'], middle['database_logger']).get_social_data(user_id)
    return {
        "social_list": list
    }


async def get_info(dialog_manager: DialogManager, **_kwargs):
    button = dialog_manager.dialog_data['social']
    return {
        "title": button[1],
        "link": button[2]
    }


async def on_click_edit(callback: CallbackQuery, _,
                        manager: DialogManager, *_kwargs):
    data = manager.middleware_data
    info = await PersonalDataHandler(data['engine'], data['database_logger']).get_social_by_id(
        int(callback.data.split(":")[-1])
    )
    manager.dialog_data['social'] = info
    await manager.switch_to(state=Social.view_link)


async def add_new(_, __, manager: DialogManager):
    buttons = [False, True, False]
    task_list = await get_data_from_db("social", manager)
    await InputForm(manager).start_dialog(buttons, task_list)


async def on_delete(_, __, manager: DialogManager):
    social_id = manager.dialog_data['social'][0]
    data = manager.middleware_data
    await PersonalDataHandler(data['engine'], data['database_logger']).delete_social_data(social_id)
    await manager.switch_to(Social.view_data)


async def on_finally(callback: CallbackQuery, _, manager: DialogManager):
    data = manager.middleware_data
    user_id = data['event_from_user'].id
    input_data = manager.dialog_data['save_input']
    await PersonalDataHandler(data['engine'], data['database_logger']).add_social_data(
        user_id, input_data['title'], input_data['link']
    )
    await callback.message.answer(f"Вы успешно добавили соц сеть - {input_data['title']}!")
    manager.show_mode = ShowMode.SEND
    await manager.switch_to(state=Social.view_data)


dialog = Dialog(
    Window(
        Const("Ваш список социальных сетей"),
        ScrollingGroup(
            Select(
                Format("{item[1]}"),
                id="scroll_social",
                items="social_list",
                item_id_getter=itemgetter(0),
                on_click=on_click_edit
            ),
            width=1,
            height=5,
            hide_on_single_page=True,
            id='scroll_profile_social',
        ),
        Row(
            Cancel(Const("< Вернуться")),
            Button(Const("Добавить +"), id="social_add", on_click=add_new),
        ),
        getter=get_data,
        state=Social.view_data
    ),
    Window(
        Const("Подтвердите добавление ссылки"),
        Button(Const("Подтвердить"), id="social_confirm", on_click=on_finally),
        Back(Const("Назад")),
        state=Social.confirm
    ),
    Window(
        Format("{title}"),
        Url(
            Const("Ссылка"),
            Format("{link}")
        ),
        Row(
            Button(Const("Удалить"), id="social_delete", on_click=on_delete),
            SwitchTo(Const("Назад"), id="social_view_back", state=Social.view_data),
        ),
        getter=get_info,
        state=Social.view_link
    ),
    on_process_result=process_input_result
)
