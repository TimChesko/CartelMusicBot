import logging
from operator import itemgetter

from aiogram.enums import ContentType
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Row, SwitchTo, ScrollingGroup, Select
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format, Const

from src.dialogs.utils.buttons import BTN_BACK, TXT_CONFIRM, TXT_REJECT, TXT_BACK
from src.dialogs.utils.common import on_start_copy_start_data
from src.utils.fsm import PersonalDataCheck


async def start_dialog_check_docs(manager: DialogManager, data: dict):
    if data['is_img'] is True:
        return await manager.start(state=PersonalDataCheck.img, data=data)
    return await manager.start(state=PersonalDataCheck.text, data=data)


async def get_data_text(dialog_manager: DialogManager, **_kwargs):
    title = dialog_manager.dialog_data['task']['title']
    value = dialog_manager.dialog_data['task']['value']
    return {
        "text": f"{title}\nОтвет: {value}"
    }


async def get_data_img(dialog_manager: DialogManager, **_kwargs):
    title = dialog_manager.dialog_data['task']['title']
    file_id = dialog_manager.dialog_data['task']['value']
    media = MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(file_id))
    return {
        "text": title,
        "media": media
    }


async def get_data_reject(dialog_manager: DialogManager, **_kwargs):
    return {
        "no_img": not dialog_manager.dialog_data['is_img']
    }


async def on_reject_edit(msg: Message, _, manager: DialogManager, __):
    column = manager.dialog_data['task']['column_name']
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    await manager.done({"confirm": False, "column": column, "edit": msg.text, "comment": None})


async def on_reject_comment(msg: Message, _, manager: DialogManager, __):
    column = manager.dialog_data['task']['column_name']
    await msg.delete()
    await manager.done({"confirm": False, "column": column, "edit": None, "comment": msg.text})


async def on_reject_template(_, __, manager: DialogManager, data):
    column = manager.dialog_data['task']['column_name']
    answers = manager.dialog_data['answers']
    result = next((item["comment"] for item in answers if item["id"] == data), None)
    await manager.done({"confirm": False, "column": column, "edit": None, "comment": result})


async def on_confirm(_, __, manager: DialogManager):
    await manager.done({"confirm": True, "column": None, "edit": None, "comment": None})


async def on_back(_, __, manager: DialogManager):
    await manager.done({"back": True})


ROW_ANSWERS = Row(
    SwitchTo(Const(TXT_REJECT), id="personal_data_reject", state=PersonalDataCheck.reject_template),
    Button(Const(TXT_CONFIRM), id="personal_data_confirm", on_click=on_confirm)
)


async def on_check_img(callback: CallbackQuery, _, manager: DialogManager):
    data = callback.data.split("_")[-1]
    result = True if data == "stop" else False
    await manager.done({"confirm": True, "stop": result})


async def on_finish(_, __, manager: DialogManager):
    await manager.done({"finish": True})


async def get_answers(dialog_manager: DialogManager, **_kwargs):
    answers = dialog_manager.dialog_data['answers']
    data = [[i["id"], i['title']] for i in answers]
    return {
        "buttons": data
    }


dialog = Dialog(
    Window(
        Format("{text}"),
        DynamicMedia(selector="media"),
        ROW_ANSWERS,
        Button(Const(TXT_BACK), id="btn_back_factory_img", on_click=on_back),
        state=PersonalDataCheck.img,
        getter=get_data_img
    ),
    Window(
        Format("{text}"),
        ROW_ANSWERS,
        Button(Const(TXT_BACK), id="btn_back_factory_txt", on_click=on_back),
        state=PersonalDataCheck.text,
        getter=get_data_text
    ),
    Window(
        Const("Выберете причину отклонения:"),
        SwitchTo(Const("Шаблонный ответ"), id="personal_data_reject_template", state=PersonalDataCheck.template),
        SwitchTo(Const("Написать комментарий"), id="personal_data_reject_comment", state=PersonalDataCheck.comment),
        SwitchTo(Const("Редактировать ответ"), id="personal_data_reject_edit",
                 when="no_img",
                 state=PersonalDataCheck.edit),
        BTN_BACK,
        state=PersonalDataCheck.reject_template,
        getter=get_data_reject
    ),
    Window(
        Const("Выберете один из ответов:"),
        ScrollingGroup(
            Select(
                Format("{item[1]}"),
                id="list_answer",
                items="buttons",
                item_id_getter=itemgetter(0),
                on_click=on_reject_template
            ),
            width=1,
            height=5,
            id='scroll_answer_with_pager',
            hide_on_single_page=True
        ),
        SwitchTo(Const(TXT_BACK), id="btn_back_from_template", state=PersonalDataCheck.reject_template),
        state=PersonalDataCheck.template,
        getter=get_answers
    ),
    Window(
        Const("Пришлите комментарий, который закрепиться за данной информацией:"),
        TextInput(id="input_comment", on_success=on_reject_comment),
        SwitchTo(Const(TXT_BACK), id="btn_back_from_comment", state=PersonalDataCheck.reject_template),
        state=PersonalDataCheck.comment
    ),
    Window(
        Const("Пришлите отредактированные данные:"),
        TextInput(id="input_comment", on_success=on_reject_edit),
        SwitchTo(Const(TXT_BACK), id="btn_back_from_edit", state=PersonalDataCheck.reject_template),
        state=PersonalDataCheck.edit
    ),
    Window(
        Const("Некоторые фотографии не прошли проверку, выберете дальнейшее действие:"),
        Button(Const("Закончить проверку"), id="personal_data_img_stop", on_click=on_check_img),
        Button(Const("Продолжить проверку"), id="personal_data_img_next", on_click=on_check_img),
        Button(Const(TXT_BACK), id="btn_back_factory_img", on_click=on_back),
        state=PersonalDataCheck.check_img,
    ),
    Window(
        Const("Закончить просмотр документа ?"),
        Row(
            Button(Const(TXT_BACK), id="btn_back_factory_img", on_click=on_back),
            Button(Const(TXT_CONFIRM), id="personal_data_finish", on_click=on_finish)
        ),
        state=PersonalDataCheck.finish
    ),
    on_start=on_start_copy_start_data,
)
