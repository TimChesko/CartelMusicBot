from operator import itemgetter

from aiogram.enums import ContentType
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import Button, Row, SwitchTo, Multiselect, ScrollingGroup, Checkbox
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format, Const

from src.dialogs.admin.tasks.personal_data.factory.model import Task
from src.dialogs.utils.buttons import TXT_CONFIRM, TXT_REJECT, TXT_BACK, BTN_BACK, TXT_NEXT
from src.dialogs.utils.common import on_start_copy_start_data
from src.utils.fsm import PersonalDataCheck


async def start_dialog_check_docs(manager: DialogManager, text: list, photo: list):
    data = {'text': text}
    if photo:
        data["photo"] = []
        for item in photo:
            data['photo'].append(Task(*item.values()).value)
    await manager.start(state=PersonalDataCheck.text, data=data, show_mode=ShowMode.SEND)


async def get_data_text(dialog_manager: DialogManager, **_kwargs):
    text = ""
    for item in dialog_manager.dialog_data['text']:
        m_item = Task(*item.values())
        text += f"{m_item.title}: {m_item.value}\n"
    if "photo" in dialog_manager.dialog_data:
        photo = dialog_manager.dialog_data["photo"]
        if "img_state" in dialog_manager.dialog_data:
            num_img = photo[0] if dialog_manager.dialog_data["img_state"] else photo[1]
        else:
            dialog_manager.dialog_data["img_state"] = True
            num_img = photo[0]
        img = MediaAttachment(ContentType.PHOTO, file_id=MediaId(num_img))
        has_img = True
    else:
        has_img = False
        img = None
    return {
        "text": text,
        "passport": img,
        "has_img": has_img
    }


async def get_buttons(dialog_manager: DialogManager, **_kwargs):
    buttons = []
    for item in dialog_manager.dialog_data['text']:
        m_item = Task(*item.values())
        buttons.append([m_item.title, m_item.column_name])
    return {
        "data": buttons,
    }


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
    manager.dialog_data['result'] = manager.find("ms_passport").get_checked()
    await manager.next()


async def on_reject(_, __, manager: DialogManager):
    await manager.done({"confirm": False, "edit": manager.dialog_data['result']})


async def on_back(_, __, manager: DialogManager):
    await manager.done({"back": True})


async def change_passport_img(_, __, manager: DialogManager):
    manager.dialog_data['img_state'] = not manager.dialog_data['img_state']


SWITCH_PHOTO = Checkbox(
    Const("1️⃣ / 2 страница"),
    Const("1 / 2️⃣ страница"),
    id="swap_passport",
    on_click=change_passport_img,
    when="has_img",
    default=True
)

dialog = Dialog(
    Window(
        DynamicMedia("passport"),
        Format("{text}"),
        SWITCH_PHOTO,
        Row(
            SwitchTo(TXT_REJECT, id="personal_data_reject", state=PersonalDataCheck.reject_data),
            Button(TXT_CONFIRM, id="personal_data_confirm", on_click=on_confirm),
        ),
        Button(TXT_BACK, id="btn_back_factory_txt", on_click=on_back),
        state=PersonalDataCheck.text,
    ),
    Window(
        DynamicMedia("passport"),
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
        SWITCH_PHOTO,
        Button(TXT_NEXT, id="finish_check", on_click=on_pre_reject),
        BTN_BACK,
        state=PersonalDataCheck.reject_data,
        getter=get_buttons
    ),
    Window(
        DynamicMedia("passport"),
        Format("{finish_text}"),
        SWITCH_PHOTO,
        Button(Const("✓ Закончить проверку"), id="finish", on_click=on_reject),
        BTN_BACK,
        state=PersonalDataCheck.finish,
        getter=get_finish_text
    ),
    getter=get_data_text,
    on_start=on_start_copy_start_data,
)
