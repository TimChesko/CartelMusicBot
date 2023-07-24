from aiogram_dialog import DialogManager

from src.models.personal_data import PersonalDataHandler


async def create_all_task(manager: DialogManager, tg_id: int) -> dict:
    middleware_ = manager.middleware_data
    data = await PersonalDataHandler(middleware_['session_maker'], middleware_['database_logger']).\
        get_all_personal_data(tg_id)
    return data


async def task_photo_and_text(all_task: dict) -> tuple[list, list]:
    all_keys = list(all_task.keys())
    photo_columns = []
    for key in all_keys:
        if key.startswith("photo_id"):
            photo_columns.append(key)
            all_keys.remove(key)
    return photo_columns, all_keys


async def load_task_dialog(manager: DialogManager, tg_id: int):
    all_task = await create_all_task(manager, tg_id)
    photo_columns, text_columns = await task_photo_and_text(all_task)
    manager.dialog_data["all_task"] = all_task
    manager.dialog_data["photo_columns"] = photo_columns
    manager.dialog_data["text_columns"] = text_columns


async def start_view_personal_data(manager: DialogManager, tg_id: int):
    await load_task_dialog(manager, tg_id)
    await start_view_personal_data()