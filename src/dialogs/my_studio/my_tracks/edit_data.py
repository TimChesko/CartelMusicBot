from aiogram.enums import ContentType
from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import TextInput, MessageInput
from aiogram_dialog.widgets.kbd import Back, Button, Row, Cancel
from aiogram_dialog.widgets.text import Const

from src.utils.fsm import StudioEdit


async def save_text(msg: Message, _, manager: DialogManager, __):
    manager.dialog_data['result'] = {"track_title": msg.text}
    await manager.switch_to(StudioEdit.confirm)


async def save_document(msg: Message, _, manager: DialogManager):
    manager.dialog_data['result'] = {"text_file_id": msg.document.file_id}
    await manager.switch_to(StudioEdit.confirm)


async def finish(_, __, manager: DialogManager):
    await manager.done(manager.dialog_data['result'])


# TEXT
async def save_document_author_text(msg: Message, _, manager: DialogManager):
    manager.dialog_data['result'] = {"words_alienation": msg.document.file_id}
    await manager.next()


async def save_percentage_text(msg: Message, _, manager: DialogManager, __):
    manager.dialog_data['result'].update({"words_author_percent": int(msg.text)})
    await manager.done(manager.dialog_data['result'])


# BEAT
async def save_document_author_beat(msg: Message, _, manager: DialogManager):
    manager.dialog_data['result'] = {"beat_alienation": msg.document.file_id}
    await manager.next()


async def save_percentage_beat(msg: Message, _, manager: DialogManager, __):
    manager.dialog_data['result'].update({"beatmaker_percent": int(msg.text)})
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
        Cancel(Const("Назад")),
        state=StudioEdit.author_text
    ),
    Window(
        Const("Какой процент от трека берет автор текста ?\nЦелое значение"),
        TextInput(
            id="input_edit_percentage",
            type_factory=int,
            on_success=save_percentage_text
        ),
        Back(Const("Назад")),
        state=StudioEdit.author_text_percent
    ),
    Window(
        Const("Пришлите отчуждение для бита"),
        MessageInput(
            func=save_document_author_beat,
            content_types=ContentType.DOCUMENT
        ),
        Cancel(Const("Назад")),
        state=StudioEdit.author_beat
    ),
    Window(
        Const("Какой процент от трека берет автор бита ?\nЦелое значение"),
        TextInput(
            id="input_edit_percentage",
            type_factory=int,
            on_success=save_percentage_beat
        ),
        Back(Const("Назад")),
        state=StudioEdit.author_beat_percent
    ),
    Window(
        Const("Подтвердить внесенные изменения ?"),
        Row(
            Back(Const("Вернуться")),
            Button(Const("Подтвердить"), id="confirm_edit", on_click=finish)
        ),
        state=StudioEdit.confirm
    )
)
