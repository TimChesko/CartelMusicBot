from operator import itemgetter

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Cancel, Button, Row
from aiogram_dialog.widgets.text import Const, Format

from src.models.personal_data import PersonalDataHandler
from src.utils.fsm import Social


async def get_data(dialog_manager: DialogManager, **_kwargs):
    middle = dialog_manager.middleware_data
    user_id = middle['event_from_user'].id
    list = await PersonalDataHandler(middle['engine'], middle['database_logger']).get_social_data(user_id)
    return {
        "social_list": list
    }


async def on_click_edit(callback: CallbackQuery, _, manager: DialogManager):
    pass


async def add_new(callback: CallbackQuery, _, manager: DialogManager):
    pass


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
    )
)
