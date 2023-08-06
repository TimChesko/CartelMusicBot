import dataclasses
from operator import itemgetter

from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button, Row, SwitchTo, Multiselect, ScrollingGroup
from aiogram_dialog.widgets.text import Format, Const

from src.dialogs.utils.buttons import TXT_CONFIRM, TXT_REJECT, TXT_BACK, BTN_BACK
from src.dialogs.utils.common import on_start_copy_start_data
from src.utils.fsm import PersonalDataCheck


@dataclasses.dataclass
class Task:
    column_id: int
    column_name: str
    title: str
    value: str


async def start_dialog_check_docs(manager: DialogManager, text: list, photo: list, callback: CallbackQuery):
    data = {'text': text}
    if photo and callback:
        data['photo'] = photo
        media = [InputMediaPhoto(media=Task(*item.values()).value) for item in photo]
        await callback.message.answer_media_group(media=media)
    await manager.start(state=PersonalDataCheck.text, data=data, show_mode=ShowMode.SEND)


async def get_data_text(dialog_manager: DialogManager, **_kwargs):
    text = ""
    for item in dialog_manager.dialog_data['text']:
        m_item = Task(*item.values())
        text += f"{m_item.title}: {m_item.value}\n"
    return {
        "text": text
    }


async def get_buttons(dialog_manager: DialogManager, **_kwargs):
    buttons = []
    for item in dialog_manager.dialog_data['text']:
        m_item = Task(*item.values())
        buttons.append([m_item.title, m_item.column_name])
    return {"data": buttons}


async def get_finish_text(dialog_manager: DialogManager, **_kwargs):
    result = dialog_manager.dialog_data['result']
    text = ""
    for item in dialog_manager.dialog_data['text']:
        m_item = Task(*item.values())
        if m_item.column_name in result:
            text += f"❌ {m_item.title}: {m_item.value}\n"
        else:
            text += f"{m_item.title}: {m_item.value}\n"
    return {
        "finish_text": text
    }


async def on_confirm(_, __, manager: DialogManager):
    await manager.done({"confirm": True, "edit": None})


async def on_pre_reject(_, __, manager: DialogManager):
    widget = manager.find("ms_passport")
    manager.dialog_data['result'] = widget.get_checked()
    await manager.next()


async def on_reject(_, __, manager: DialogManager):
    await manager.done({"confirm": False, "edit": manager.dialog_data['result']})


async def on_back(_, __, manager: DialogManager):
    await manager.done({"back": True})


dialog = Dialog(
    Window(
        Format("{text}"),
        Row(
            SwitchTo(TXT_REJECT, id="personal_data_reject", state=PersonalDataCheck.reject_data),
            Button(TXT_CONFIRM, id="personal_data_confirm", on_click=on_confirm),
        ),
        Button(TXT_BACK, id="btn_back_factory_txt", on_click=on_back),
        state=PersonalDataCheck.text,
    ),
    Window(
        Format("{text}\n\nВыберете информацию, которую нужно отклонить:"),
        ScrollingGroup(
            Multiselect(
                Format("✓ {item[0]}"),
                Format("{item[0]}"),
                id="ms_passport",
                items="data",
                item_id_getter=itemgetter(1),
            ),
            width=1,
            height=5,
            id="scroll_with_pager_personal_data",
            hide_on_single_page=True
        ),
        Button(Const("Продолжить"), id="finish_check", on_click=on_pre_reject),
        BTN_BACK,
        state=PersonalDataCheck.reject_data,
        getter=get_buttons
    ),
    Window(
        Format("{finish_text}"),
        Button(Const("Закончить проверку"), id="finish", on_click=on_reject),
        BTN_BACK,
        state=PersonalDataCheck.finish,
        getter=get_finish_text
    ),
    getter=get_data_text,
    on_start=on_start_copy_start_data,
)
