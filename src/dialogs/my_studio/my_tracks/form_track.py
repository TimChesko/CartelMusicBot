from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.widgets.text import Const

from src.utils.fsm import TrackApprove

dialog = Dialog(
    Window(
        Const("Подтвердите название трека"),
        Button(Const("Назад")),
        Button(Const("Подтвердить")),
        state=TrackApprove.name
    ),
    Window(
        # TODO Текст трека скидывают на стадии модерации
        Const("Подтвердите текст трека"),
        Button(Const("Назад")),
        Button(Const("Подтвердить")),
        state=TrackApprove.text
    ),
    Window(
        # TODO Другой человек - новый диалог в done передать данные
        Const("Автор бита"),
        Button(Const("Другой человек")),
        Button(Const("Я и есть автор")),
        state=TrackApprove.author_music
    ),
    Window(
        # TODO Другой человек - новый диалог в done передать данные
        Const("Автор текста"),
        Button(Const("Другой человек")),
        Button(Const("Я и есть автор")),
        state=TrackApprove.author_text
    ),
    Window(
        Const("Время трека"),
        TextInput(),
        state=TrackApprove.time_track
    ),
    Window(
        Const("Наличие нецензурной лексики"),
        Button(Const("Не имеется")),
        Button(Const("Имеется")),
        state=TrackApprove.profanity
    ),
    Window(
        # TODO Да - новый диалог в done передать данные
        Const("Тип трека - фит ?"),
        Button(Const("Да")),
        Button(Const("Это не фит")),
        state=TrackApprove.fit
    ),
    # TODO заполнение промо
    # TODO если фит скинуть ссылку для юзера с уточнением, что тот должен пройти регистрацию
    # TODO отправить на модерацию, с ожиданием прихода автора фита
)
