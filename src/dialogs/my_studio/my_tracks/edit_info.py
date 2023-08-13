from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Button, Row
from aiogram_dialog.widgets.text import Const

from src.dialogs.utils.buttons import BTN_BACK, BTN_CANCEL_BACK, TXT_CONFIRM
from src.utils.fsm import StudioEdit


async def save_text(msg: Message, _, manager: DialogManager, __):
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    manager.dialog_data['result'] = {"title": msg.text}
    await manager.switch_to(StudioEdit.confirm)


async def save_document(msg: Message, _, manager: DialogManager):
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    manager.dialog_data['result'] = {"text_file_id": msg.document.file_id}
    await manager.switch_to(StudioEdit.confirm)


async def finish(_, __, manager: DialogManager):
    await manager.done(manager.dialog_data['result'])


# TEXT
async def save_document_author_text(msg: Message, _, manager: DialogManager):
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    manager.dialog_data['result'] = {"words_alienation": msg.document.file_id}
    await manager.next()


async def save_fullname_text(msg: Message, _, manager: DialogManager, __):
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    manager.dialog_data['result'].update({"words_author_fullname": msg.text})
    await manager.done(manager.dialog_data['result'])


# BEAT
async def save_document_author_beat(msg: Message, _, manager: DialogManager):
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    manager.dialog_data['result'] = {"beat_alienation": msg.document.file_id}
    await manager.next()


async def save_fullname_beat(msg: Message, _, manager: DialogManager, __):
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    manager.dialog_data['result'].update({"beatmaker_fullname": int(msg.text)})
    await manager.done(manager.dialog_data['result'])


async def save_percentage_feat(msg: Message, _, manager: DialogManager, __):
    await msg.delete()
    manager.show_mode = ShowMode.EDIT
    manager.dialog_data['result'] = {"feat_status": True, "feat_percent": int(msg.text)}
    await manager.done(manager.dialog_data['result'])


dialog = Dialog(
    Window(
        Const("Пришлите новое название для трека"),
        TextInput(
            id="input_edit_title",
            on_success=save_text
        ),
        state=StudioEdit.title
    ),
    Window(
        Const("Пришлите отчуждение для текста"),
        MessageInput(
            func=save_document_author_text,
            content_types=ContentType.DOCUMENT
        ),
        BTN_CANCEL_BACK,
        state=StudioEdit.author_text
    ),
    Window(
        Const("Полное ФИО автора текста ?"),
        TextInput(
            id="input_edit_percentage",
            type_factory=int,
            on_success=save_fullname_text
        ),
        BTN_BACK,
        state=StudioEdit.author_text_percent
    ),
    Window(
        Const("Пришлите отчуждение для бита"),
        MessageInput(
            func=save_document_author_beat,
            content_types=ContentType.DOCUMENT
        ),
        BTN_CANCEL_BACK,
        state=StudioEdit.author_beat
    ),
    Window(
        Const("Полное ФИО автора бита ?"),
        TextInput(
            id="input_edit_beatmaker_percent",
            type_factory=int,
            on_success=save_fullname_beat
        ),
        BTN_BACK,
        state=StudioEdit.author_beat_percent
    ),
    Window(
        Const("Какой процент от трека берет участник фита ?\nЦелое значение"),
        TextInput(
            id="input_edit_percentage_feat",
            type_factory=int,
            on_success=save_percentage_feat
        ),
        BTN_BACK,
        state=StudioEdit.feat_percent
    ),
    Window(
        Const("Подтвердить внесенные изменения ?"),
        Row(
            BTN_BACK,
            Button(TXT_CONFIRM, id="confirm_edit", on_click=finish)
        ),
        state=StudioEdit.confirm
    )
)
