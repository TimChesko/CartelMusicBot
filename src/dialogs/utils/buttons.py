from dataclasses import dataclass

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


@dataclass
class TxtApprovement:
    title: str
    reason: str = None

    def listening_approve(self):
        return (f'Отличные новости! Ваш трек <b>"{self.title}"</b> '
                f'успешно прошёл этап прослушивания. 🎧🎶\n'
                f'Теперь пришло время поделиться вашим творчеством с аудиторией.\n'
                f'Просто перейдите в раздел\n <b>"💠 Моя студия"</b> ➡️ <b>"🎧 Список треков"</b>'
                f'и дополните информацию о треке в разделе <b>"✅ Принятые"</b>.\n'
                f' Этот важный шаг поможет выгрузить ваш трек на площадку и открыть его для мира! 🚀')

    def listening_reject(self):
        return (f'Ваш трек <b>"{self.title}"</b>'
                f' был отклонен с комментарием:\n {self.reason}.\n'
                f'Не переживайте, вы можете внести изменения и'
                f' отправить его на повторное прослушивание! 🎵🔧')

    def release_reject(self):
        return (f'К сожалению, мы обнаружили некоторые недоработки в вашем релизе'
                f' <b>"{self.title}"</b>.🛑🎶\n'
                f'{self.reason}\n'
                f'Не беспокойтесь, это всего лишь этап.'
                f' После внесения изменений, вы сможете отправить релиз на повторное рассмотрение.'
                f'Не сдавайтесь - ваше творчество стоит того, чтобы продолжать работу над ним. Удачи! 🎵🔧')

    def release_approve(self):
        return (f'Ваш релиз <b>"{self.title}"</b> успешно прошёл нашу проверку! 🎉🎵\n'
                f'Данные в полном порядке👍. Пройдите в <b>"📨 Выпустить трек в продакшн"</b>,'
                f' чтобы продолжить работать с релизом')

    def release_finish(self):
        return (f'Отличные новости! Ваш релиз <b>"{self.title}"</b> '
                f'успешно прошёл нашу проверку! 🎉🎵\n'
                f'Все данные в абсолютном порядке👍. Теперь ваш релиз готов к следующему'
                f' этапу. Он будет отгружен в указанные даты,'
                f' так что вы можете считать свою работу с ним завершенной.\n'
                f'Вы можете найти данные по релизу в разделе <b>"Мои релизы"</b>.\n'
                f'Большое спасибо за ваше участие! 🚀🎶')


async def coming_soon(callback: CallbackQuery, __, _):
    await callback.answer('Coming soon...')
