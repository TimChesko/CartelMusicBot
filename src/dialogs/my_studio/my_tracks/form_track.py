import logging
from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Back, Row, Next
from aiogram_dialog.widgets.text import Const

from src.dialogs.utils.common import on_start_copy_start_data
from src.utils.fsm import TrackApprove


async def on_start(data: Any, manager: DialogManager):
    await on_start_copy_start_data(data, manager)
    manager.dialog_data['track'] = {}


async def save_data_callback(callback: CallbackQuery, _, manager: DialogManager):
    dialog_data = manager.dialog_data
    data = callback.data.split("_")
    dialog_data["track"][data[1]] = data[2]


async def save_data_message(msg: Message, _, manager: DialogManager):
    pass


dialog = Dialog(
    Window(
        Const("Подтвердите название трека"),
        Row(
            Back(Const("Назад")),
            Next(Const("Подтвердить")),
        ),
        state=TrackApprove.name
    ),
    Window(
        # TODO Текст трека скидывают на стадии модерации
        Const("Подтвердите текст трека"),
        Row(
            Back(Const("Назад")),
            Next(Const("Подтвердить")),
        ),
        state=TrackApprove.text
    ),
    Window(
        # TODO Другой человек - новый диалог в done передать данные
        Const("Автор бита"),
        Row(
            Button(Const("Другой человек"), id="track_music_other", on_click=...),
            Button(Const("Я и есть автор"), id="track_music_author", on_click=save_data_callback),
        ),
        Back(Const("Назад")),
        state=TrackApprove.author_music
    ),
    Window(
        # TODO Другой человек - новый диалог в done передать данные
        Const("Автор текста"),
        Row(
            Button(Const("Другой человек"), id="track_text_other", on_click=...),
            Button(Const("Я и есть автор"), id="track_text_author", on_click=save_data_callback),
        ),
        Back(Const("Назад")),
        state=TrackApprove.author_text
    ),
    Window(
        Const("Время трека\nПример: 1:23"),
        TextInput(
            id="track_time",
            on_success=save_data_message,
        ),
        state=TrackApprove.time_track
    ),
    Window(
        Const("Наличие нецензурной лексики"),
        Button(Const("Не имеется"), id="track_profanity_false", on_click=save_data_callback),
        Button(Const("Имеется"), id="track_profanity_true", on_click=save_data_callback),
        state=TrackApprove.profanity
    ),
    Window(
        Const("Тип трека - фит ?"),
        Button(Const("Да"), id="track_feat_true", on_click=save_data_callback),
        Button(Const("Это не фит"), id="track_feat_false", on_click=save_data_callback),
        state=TrackApprove.feat
    ),
    # TODO заполнение промо
    # TODO если фит скинуть ссылку для юзера с уточнением, что тот должен пройти регистрацию
    # TODO отправить на модерацию, с ожиданием прихода автора фита
    on_start=on_start
)
