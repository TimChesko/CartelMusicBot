from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from src.dialogs.utils.buttons import BTN_CANCEL_BACK
from src.utils.fsm import AdminRelease, AdminReleaseLvl1, \
    AdminReleaseLvl2, AdminReleaseLvl3

# TODO сделать в названии отображение кол-ва заявок

main = Dialog(
    Window(
        Const("Тут находятся все проверки связанные с лицензионным договором\n"
              "Они делятся на три типа:\n"
              "1) Проверка обложки, названия альбома, списка треков и первичного лицензионного договора\n"
              "2) Проверка подписи лицензионного договора\n"
              "2) Проверка трек номера CDEK"),
        Start(Const('📝Первичная'), state=AdminReleaseLvl1.start, id='lvl1_start'),
        Start(Const('✍Подпись'), state=AdminReleaseLvl2.start, id='lvl2_start'),
        Start(Const('📩Трек номер'), state=AdminReleaseLvl3.start, id='lvl3_start'),
        BTN_CANCEL_BACK,
        state=AdminRelease.menu
    )
)
