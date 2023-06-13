from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


async def markup_start() -> ReplyKeyboardMarkup:
    menu = ReplyKeyboardBuilder()

    menu.button(text='Отправить трек на прослушивание')
    menu.button(text='*Кнопки с услугами* ')

    menu.adjust(2, True)
    return menu.as_markup(resize_keyboard=True)