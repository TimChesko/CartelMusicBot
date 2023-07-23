from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Start, Cancel
from aiogram_dialog.widgets.text import Const

from src.utils.fsm import AdminTemplates, TemplatesListening

template_menu = Dialog(
    Window(
        Const('Шаблоны'),
        Start(Const('Прослушивание'),
              id='admin_templates',
              state=TemplatesListening.start),
        Cancel(Const('Главное меню')),
        state=AdminTemplates.start
    ),
)