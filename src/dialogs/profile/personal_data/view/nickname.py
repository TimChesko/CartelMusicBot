from aiogram_dialog import DialogManager

from src.dialogs.utils.widgets.input_forms.process_input import InputForm


async def start_edit_nickname(manager: DialogManager):
    buttons = [False, True, False]
    task_list = {"edit_nickname": {
        "data_name": "edit_nickname",
        "title": "Никнейм",
        "text": "Пришлите ваш новый никнейм\n\nПример: getxp",
        "input_type": ["any"],
        "comment": None
    }
    }
    await InputForm(manager).start_dialog(buttons, task_list)
