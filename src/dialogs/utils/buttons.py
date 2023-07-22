from aiogram_dialog.widgets.kbd import Cancel, Back
from aiogram_dialog.widgets.text import Const

# TEXT
TXT_BACK = "‹ Назад"
TXT_REJECT = "✘ Отклонить"
TXT_CONFIRM = "✓ Принять"

# BUTTONS
BTN_CANCEL_BACK = Cancel(Const(TXT_BACK))
BTN_BACK = Back(Const(TXT_BACK))
