from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from src.dialogs.utils.buttons import BTN_CANCEL_BACK
from src.utils.fsm import AdminTemplates, TemplatesListening

template_menu = Dialog(
    Window(
        Const('Шаблоны'),
        Start(Const('Прослушивание'),
              id='admin_templates',
              state=TemplatesListening.start),
        BTN_CANCEL_BACK,
        state=AdminTemplates.start
    ),
)