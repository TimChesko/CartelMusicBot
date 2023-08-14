import logging
from operator import itemgetter

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import ScrollingGroup, Select, Button, Row, Url, SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from src.dialogs.utils.buttons import TXT_BACK, TXT_APPROVE, BTN_CANCEL_BACK
from src.dialogs.utils.widgets.input_forms.process_input import process_input_result, InputForm
from src.dialogs.utils.widgets.input_forms.utils import get_data_from_db
from src.dialogs.utils.widgets.input_forms.window_input import start_dialog_filling_profile
from src.models.personal_data import PersonalDataHandler
from src.utils.fsm import Social


async def get_data(dialog_manager: DialogManager, **_kwargs):
    middle = dialog_manager.middleware_data
    user_id = middle['event_from_user'].id
    social_list = await PersonalDataHandler(middle['session_maker'], middle['database_logger']).get_social_data(user_id)
    return {
        "social_list": social_list
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
    info = await PersonalDataHandler(data['session_maker'], data['database_logger']).get_social_by_id(
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
    await PersonalDataHandler(data['session_maker'], data['database_logger']).delete_social_data(social_id)
    await manager.switch_to(Social.view_data)


async def on_finally(callback: CallbackQuery, _, manager: DialogManager):
    data = manager.middleware_data
    support = data['config'].constant.support
    user_id = data['event_from_user'].id
    input_data = manager.dialog_data['save_input']
    logging.debug(input_data)
    answer = await PersonalDataHandler(data['session_maker'], data['database_logger']).add_social_data(
        user_id, input_data['title']['value'], input_data['link']['value']
    )
    if answer:
        text = f"✅ Вы успешно добавили соц сеть - {input_data['title']['value']}!"
    else:
        text = f'❌ Произошел сбой на стороне сервера. Обратитесь в поддержку {support}'
    await callback.message.edit_text(text)
    manager.show_mode = ShowMode.SEND
    await manager.switch_to(state=Social.view_data)


async def back_dialog(_, __, manager: DialogManager):
    task_list_done = manager.dialog_data["task_list_done"]
    task_list_process = manager.dialog_data["task_list_process"]
    manager.current_context().state = Social.view_data
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


dialog = Dialog(
    Window(
        Const("⭐️ Социальные сети\n"),
        Const("❓ Данные соц. сети будут прикреплены к альбомам, которые Вы выпустите"),
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
            BTN_CANCEL_BACK,
            Button(Const("Добавить +"), id="social_add", on_click=add_new),
        ),
        getter=get_data,
        state=Social.view_data
    ),
    Window(
        Format("{text}"),
        Const("🔰 Проверьте и подтвердите правильность данных"),
        Button(TXT_APPROVE, id="social_confirm", on_click=on_finally),
        Button(TXT_BACK, id="social_back", on_click=back_dialog),
        state=Social.confirm,
        getter=get_finish_data,
        disable_web_page_preview=True
    ),
    Window(
        Format("Название соц сети: {title}"),
        Url(
            Const("Ссылка"),
            Format("{link}")
        ),
        Row(
            SwitchTo(TXT_BACK, id="social_view_back", state=Social.view_data),
            Button(Const("Удалить"), id="social_delete", on_click=on_delete),
        ),
        getter=get_info,
        state=Social.view_link,
        disable_web_page_preview=True
    ),
    on_process_result=process_input_result
)
