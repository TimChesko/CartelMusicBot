from aiogram.types import CallbackQuery
from aiogram_dialog.widgets.kbd import Cancel, Back
from aiogram_dialog.widgets.text import Const

# TEXT
TXT_BACK = Const("‹ Назад")
TXT_NEXT = Const("Продолжить ›")
TXT_REJECT = Const("✘ Отклонить")
TXT_CONFIRM = Const("✓ Принять")
TXT_FALSE = Const("✘ Нет")
TXT_TRUE = Const("✓ Да")
TXT_CANCEL = Const("✘ Отменить")
TXT_APPROVE = Const("✓ Подтвердить")
TXT_EDIT = Const("✍ Изменить")

# BUTTONS
BTN_CANCEL_BACK = Cancel(TXT_BACK)
BTN_BACK = Back(TXT_BACK)


async def coming_soon(callback: CallbackQuery, __, _):
    await callback.answer('Coming soon...')
