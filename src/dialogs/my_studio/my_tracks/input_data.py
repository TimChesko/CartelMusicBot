from aiogram.types import Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Row, Counter
from aiogram_dialog.widgets.text import Const, Progress

from src.utils.fsm import TrackAuthor

async def save_data_message(msg: Message, _, manager: DialogManager):



dialog = Dialog(
    Window(
        Const("Выберете тип соглашения с автором"),
        Row(
            Button(Const("Отчуждение")),
            Button(Const("Что это ?")),
        ),
        Button(Const("По процентам")),
        state=TrackAuthor.type_agreement
    ),
    Window(
        Const("Напишите сколько процентов отдается автору"),
        TextInput(
            id="track_author_percentage",
            type_factory=int,
            on_success=save_data_message
        ),
        state=TrackAuthor.percentage
    ),
)