from aiogram.utils.keyboard import InlineKeyboardBuilder


def markup_new_listening(track_id):
    approvement = InlineKeyboardBuilder()

    approvement.button(text='Одобрить', callback_data=f'listening_approve_{track_id}')
    approvement.button(text='Одобрить с промо', callback_data=f'listening_approve-promo_{track_id}')
    approvement.button(text='Отклонить шаблон', callback_data=f'listening_pattern-reject_{track_id}')
    approvement.button(text='Отклонить с ответом', callback_data=f'listening_answer-reject_{track_id}')

    approvement.adjust(1)
    return approvement.as_markup()


def markup_reject_patterns(track_id):
    reasons = InlineKeyboardBuilder()

    reasons.button(text='Бездарный', callback_data=f'listening_reason-idiot_{track_id}')
    reasons.button(text='Плохо сведено', callback_data=f'listening_reason-mixing_{track_id}')
    reasons.button(text='Нас посадят', callback_data=f'listening_reason-incorrect_{track_id}')
    reasons.button(text='Уже отправлял', callback_data=f'listening_reason-alrdy-was_{track_id}')
    reasons.button(text='Назад', callback_data=f'listening_back-new_{track_id}')

    reasons.adjust(1)
    return reasons.as_markup()


def markup_edit_listening(track_id):
    approvement = InlineKeyboardBuilder()

    approvement.button(text='Одобрить', callback_data=f'listening_approve-edit_{track_id}')
    approvement.button(text='Одобрить с промо', callback_data=f'listening_approve-promo-edit_{track_id}')
    approvement.button(text='Отклонить шаблон', callback_data=f'listening_pattern-reject-edit_{track_id}')
    approvement.button(text='Отклонить с ответом', callback_data=f'listening_answer-reject-edit_{track_id}')

    approvement.adjust(1)
    return approvement.as_markup()


def markup_edit_reject_patterns(track_id):
    reasons = InlineKeyboardBuilder()

    reasons.button(text='Бездарный', callback_data=f'listening_reason-idiot-edit_{track_id}')
    reasons.button(text='Плохо сведено', callback_data=f'listening_reason-mixing-edit_{track_id}')
    reasons.button(text='Нас посадят', callback_data=f'listening_reason-incorrect-edit_{track_id}')
    reasons.button(text='Уже отправлял', callback_data=f'listening_reason-alrdy-was-edit_{track_id}')
    reasons.button(text='Назад', callback_data=f'listening_back-edit_{track_id}')

    reasons.adjust(1)
    return reasons.as_markup()
