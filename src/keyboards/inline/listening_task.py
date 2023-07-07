from aiogram.utils.keyboard import InlineKeyboardBuilder


def markup_listening(user_id):
    task = InlineKeyboardBuilder()

    task.button(text='Взять таск', callback_data=f'listening_accept_{user_id}')

    task.adjust(2)
    return task.as_markup()
