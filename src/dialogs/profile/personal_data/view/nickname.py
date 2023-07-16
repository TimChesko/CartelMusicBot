from aiogram_dialog import DialogManager

from src.utils.fsm import DialogInput


async def start_edit_nickname(manager: DialogManager, error: str = None):
    data = {"data_type": "edit_nickname",
            "request": "Пришлите ваш новый никнейм",
            "example": "Пример: getxp",
            "error": error}
    await manager.start(state=DialogInput.text, data=data)
