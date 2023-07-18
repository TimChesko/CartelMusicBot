from aiogram_dialog import DialogManager

from src.dialogs.utils.widgets.input_forms.process_input import InputForm
from src.utils.fsm import DialogInput


async def start_edit_nickname(manager: DialogManager):
    buttons = [True, True, True]
    task_list = {"edit_nickname": {
        "data_name": "edit_nickname",
        "title": "Никнейм",
        "text": "Пришлите ваш новый никнейм\n\nПример: getxp",
        "input_type": ["any"]
          }
    }
    await InputForm(manager).start_dialog(buttons, task_list)
