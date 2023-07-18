from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

dialog = Dialog(
    Window(
        Const("Выберете категорию"),
        Start(Const("Статус публикаций"), id="studio_status_public", when=..., state=...),
        Start(Const("Список треков"), id="studio_list_tracks", when=..., state=...),
    )
)
